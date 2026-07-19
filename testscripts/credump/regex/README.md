# CreDump

**CreDump** is a powerful Python-based CLI tool to discover sensitive file endpoints and extract credentials/secrets from programmatic files like `.js`, `.php`, `.json`, etc. It supports multithreading, filtering, and even optional live secret validation.

---

### Features

- Detects sensitive files like `.env`, `.git/config`, `config.json`, etc.
- Greps credentials from HTML/JS/PHP/JSON files using regex rules
- Wildcard extension testing (e.g., `index` → `index.js`, `index.json`, ...)
- **Filters:**
  - HTTP status code (`--status`)
  - Content-Type (`--content-type`)
  - Response body content (`--contains`)
- Multi-threaded for fast scanning (`--threads`)
-  Optional validation of secrets like:
  - AWS keys (manual guidance)
  - Slack Webhooks (live test via `POST`)
-  Proxy support (`--proxy`)
-  Supports both `--urlfile` and STDIN input

---

## 🚀 Installation

```bash
git clone https://github.com/yourname/credleak-scanner.git
cd credleak-scanner
pip install -r requirements.txt
```


Requirements

- requests
- PyYAML
- colorama

🧪 Usage
🔹 Find Sensitive Files
```bash
python3 scanner.py -file -u urls.txt
```
🔹 Grep for Secrets in Program Files
```bash
python3 scanner.py -cred -u urls.txt
```
🔹 Use Standard Input
```bash
cat urls.txt | python3 scanner.py -cred
```
🔹 Advanced Options
```bash
--threads 20                     # Number of threads (default: 10)
--status 200                     # Only show HTTP 200 results
--content-type text/plain        # Match content-type
--contains aws_access_key        # Body must contain string
--proxy http://127.0.0.1:8080    # Route requests through proxy
```