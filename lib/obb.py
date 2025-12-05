import os
import requests
from bs4 import BeautifulSoup
from time import sleep
from colorama import Fore, init

init(autoreset=True)

BASE_URL = "https://www.openbugbounty.org"
AJAX_URL = f"{BASE_URL}/bugbounty-list/ajax.php"

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Content-Type": "application/x-www-form-urlencoded",
    "Referer": "https://www.openbugbounty.org/bugbounty-list/"
}

RES_OBB_DIR = "res/obb"
os.makedirs(RES_OBB_DIR, exist_ok=True)


def get_all_programs():
    """Fetch all OpenBugBounty programs using AJAX paginated endpoint."""
    programs = []
    start = 0
    page = 1

    while True:
        print(f"{Fore.YELLOW}[>] Fetching page {page} (start={start})")
        data = {
            "draw": "1",
            "columns[0][data]": "0",
            "columns[1][data]": "1",
            "columns[2][data]": "2",
            "start": start,
            "length": 50,
        }

        try:
            res = requests.post(AJAX_URL, headers=HEADERS, data=data, timeout=10)
            res.raise_for_status()
            json_data = res.json()

            rows = json_data.get("data", [])
            if not rows:
                break

            for row in rows:
                soup = BeautifulSoup(row[0], "html.parser")
                a = soup.find("a", href=True)
                if a and "/bugbounty/" in a["href"]:
                    name = a.text.strip()
                    url = BASE_URL + a["href"]
                    print(f"{Fore.GREEN}[+] Program: {name}")
                    programs.append({"name": name, "url": url})

            start += 50
            page += 1

        except Exception as e:
            print(f"{Fore.RED}[!] Error on page {page}: {e}")
            break

    print(f"{Fore.CYAN}[✓] Total programs extracted: {len(programs)}")
    return programs


def get_scope_domains(program_url):
    """Extract domain scope from program page."""
    print(f"{Fore.YELLOW}[>] Scope: {program_url}")
    domains = []

    try:
        res = requests.get(program_url, headers=HEADERS, timeout=10)
        res.raise_for_status()
        soup = BeautifulSoup(res.text, "html.parser")
        table = soup.find("table", class_="wishlist open-bounty")
        if not table:
            print(f"{Fore.RED}    [!] No scope table found")
            return []

        for tr in table.find_all("tr")[1:]:
            td = tr.find("td")
            if td:
                domain = td.text.strip()
                print(f"{Fore.BLUE}    [+] {domain}")
                domains.append(domain)

        return domains

    except Exception as e:
        print(f"{Fore.RED}[!] Failed to fetch scope: {e}")
        return []


def save_obb(domains):
    out_file = os.path.join(RES_OBB_DIR, "domains.txt")
    with open(out_file, "w") as f:
        for d in domains:
            f.write(d + "\n")
    return out_file


def run_obb():
    """Main function called by send.py — scrapes and returns saved OBB file path."""
    programs = get_all_programs()

    all_domains = set()
    for idx, program in enumerate(programs):
        print(f"{Fore.MAGENTA}[{idx+1}/{len(programs)}] {program['name']}")
        scope = get_scope_domains(program["url"])
        for d in scope:
            all_domains.add(d)
        sleep(1)

    # Save output
    out_file = save_obb(sorted(all_domains))
    print(f"{Fore.GREEN}[✓] Saved to {out_file}")
    return out_file
