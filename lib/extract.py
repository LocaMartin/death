# lib/extract.py

import re
from pathlib import Path

OUT_DIR = Path("out")
RES_DIR = Path("res")

OUT_DIR.mkdir(exist_ok=True)
RES_DIR.mkdir(exist_ok=True)

CATS = {
    "domain": set(),
    "url": set(),
    "ip": set(),
    "cidr": set(),
    "wildcard": set()
}

def categorize(line):
    line = line.strip()
    if not line: return None

    if re.match(r"^https?://", line, re.I): return "url"
    if re.match(r"^\d{1,3}(\.\d{1,3}){3}/\d{1,2}$", line): return "cidr"
    if re.match(r"^\d{1,3}(\.\d{1,3}){3}$", line): return "ip"
    if re.match(r"^\*\.[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", line): return "wildcard"
    if re.match(r"^[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", line): return "domain"
    return None


def merge_targets():
    for key in CATS:
        CATS[key].clear()

    for f in OUT_DIR.glob("*"):
        try:
            f.unlink()
        except Exception:
            pass
        
    for file in RES_DIR.rglob("*.txt"):
        for line in open(file, errors="ignore"):
            cat = categorize(line)
            if cat:
                CATS[cat].add(line.strip())

    output_map = {
        "domain": "domains.txt",
        "url": "urls.txt",
        "ip": "ips.txt",
        "cidr": "cidr.txt",
        "wildcard": "wildcards.txt",
    }

    log = ["[+] Merging extracted scope targets"]

    for key, filename in output_map.items():
        out_file = OUT_DIR / filename
        values = sorted(CATS[key])
        with open(out_file, "w") as f:
            f.write("\n".join(values))
        log.append(f" → {filename}: {len(values)} items")

    log.append("[OK] Merge completed")
    return "\n".join(log)
