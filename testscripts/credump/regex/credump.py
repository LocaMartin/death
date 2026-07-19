#!/usr/bin/env python3

import requests
import yaml
import re
import argparse
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urljoin
from colorama import Fore, Style, init

# Disable SSL warnings
requests.packages.urllib3.disable_warnings()
init(autoreset=True)  # Initialize colorama

def load_yaml(file_path):
    with open(file_path, 'r') as f:
        return yaml.safe_load(f)

def load_urls(file_path):
    with open(file_path, 'r') as f:
        return [url.strip().rstrip('/') for url in f if url.strip()]

def load_stdin_urls():
    return [line.strip().rstrip('/') for line in sys.stdin if line.strip()]

def build_wildcard_urls(base_urls, sensitive_paths):
    urls = []
    for base in base_urls:
        for entry in sensitive_paths:
            url = f"{base}/{entry['path']}"
            urls.append((url, entry['description']))
    return urls

def build_program_file_urls(base_urls):
    extensions = ['.html', '.js', '.php', '.json']
    urls = []
    for base in base_urls:
        for ext in extensions:
            if not base.endswith(ext):
                urls.append(f"{base}{ext}")
            else:
                urls.append(base)
    return list(set(urls))

def match_filters(response, filters):
    if filters['status'] and response.status_code != int(filters['status']):
        return False
    if filters['content_type'] and filters['content_type'] not in response.headers.get('Content-Type', ''):
        return False
    if filters['contains'] and filters['contains'] not in response.text:
        return False
    return True

def scan_file_endpoint(session, url, description, filters):
    try:
        resp = session.get(url, timeout=10, verify=False)
        if resp.status_code == 200 and match_filters(resp, filters):
            return f"{Fore.GREEN}[+] {url}{Style.RESET_ALL} — {description}"
    except requests.RequestException:
        return None

def validate_secret(name, match):
    if name == "AWS Access Key":
        return f"{Fore.YELLOW}[!] Potential AWS Access Key found — validate manually with sts:GetCallerIdentity{Style.RESET_ALL}"
    elif name == "Slack Webhook":
        try:
            resp = requests.post(match, json={"text": "Validation test from scanner"}, timeout=5)
            if resp.status_code == 200:
                return f"{Fore.CYAN}[✓] Valid Slack Webhook: {match}{Style.RESET_ALL}"
            else:
                return f"{Fore.YELLOW}[!] Slack Webhook responded with status {resp.status_code}{Style.RESET_ALL}"
        except:
            return f"{Fore.RED}[!] Slack Webhook request failed: {match}{Style.RESET_ALL}"
    return None

def grep_credential_patterns(session, url, grep_rules, filters):
    try:
        resp = session.get(url, timeout=10, verify=False)
        if resp.status_code == 200 and match_filters(resp, filters):
            content = resp.text
            findings = []
            for rule in grep_rules:
                matches = re.findall(rule['pattern'], content)
                if matches:
                    findings.append(f"{Fore.GREEN}[+] {rule['name']} found at {url}{Style.RESET_ALL} — {rule['description']}")
                    for match in matches:
                        findings.append(f"    └─ {Fore.MAGENTA}{str(match)[:100]}{Style.RESET_ALL}")
                        validation = validate_secret(rule['name'], match)
                        if validation:
                            findings.append(f"        → {validation}")
            return '\n'.join(findings) if findings else None
    except requests.RequestException:
        return None

def main():
    parser = argparse.ArgumentParser(description="Sensitive File & Credential Finder Tool")
    parser.add_argument("-file", help="Find sensitive file endpoints", action='store_true')
    parser.add_argument("-cred", help="Grep sensitive info/credentials from program file endpoints", action='store_true')
    parser.add_argument("-u", "--urlfile", help="Path to URLs list (or use stdin)")
    parser.add_argument("--threads", type=int, default=10, help="Number of threads (default: 10)")
    parser.add_argument("--status", help="Filter by HTTP status code")
    parser.add_argument("--content-type", help="Filter by Content-Type")
    parser.add_argument("--contains", help="Response must contain this string")
    parser.add_argument("--proxy", help="Proxy like http://127.0.0.1:8080")
    parser.add_argument("--file-yaml", default="sensitive-files.yaml", help="YAML with sensitive file paths")
    parser.add_argument("--grep-yaml", default="sensitive-grep-rules.yaml", help="YAML with credential grep rules")

    args = parser.parse_args()
    filters = {
        'status': args.status,
        'content_type': args.content_type,
        'contains': args.contains
    }

    proxies = {"http": args.proxy, "https": args.proxy} if args.proxy else None

    urls = load_urls(args.urlfile) if args.urlfile else load_stdin_urls()

    session = requests.Session()
    if proxies:
        session.proxies.update(proxies)

    tasks = []
    results = []

    with ThreadPoolExecutor(max_workers=args.threads) as executor:
        if args.file:
            sensitive_data = load_yaml(args.file_yaml)['sensitive_files']
            target_urls = build_wildcard_urls(urls, sensitive_data)
            for url, desc in target_urls:
                tasks.append(executor.submit(scan_file_endpoint, session, url, desc, filters))

        elif args.cred:
            grep_rules = load_yaml(args.grep_yaml)['grep_rules']
            target_urls = build_program_file_urls(urls)
            for url in target_urls:
                tasks.append(executor.submit(grep_credential_patterns, session, url, grep_rules, filters))

        for future in as_completed(tasks):
            result = future.result()
            if result:
                print(result)

if __name__ == "__main__":
    main()
