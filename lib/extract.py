# lib/extract.py

import re
from pathlib import Path

OUT_DIR = Path("out")
RES_DIR = Path("res")

CATS = {
    "domain": set(),
    "url": set(),
    "ip": set(),
    "cidr": set(),
    "wildcard": set()
}

def categorize(line: str):
    line = line.strip()

    if not line:
        return None

    # URL
    if re.match(r"^https?://", line, re.I):
        return "url"

    # CIDR
    if re.match(r"^\d{1,3}(\.\d{1,3}){3}/\d{1,2}$", line):
        return "cidr"

    # IP
    if re.match(r"^\d{1,3}(\.\d{1,3}){3}$", line):
        return "ip"

    # Wildcard domain
    if re.match(r"^\*\.[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", line):
        return "wildcard"

    # Domain
    if re.match(r"^[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", line):
        return "domain"

    return None


def merge_targets():
    """Reads everything in res/ and outputs into out/ directory."""
    # clear previous
    OUT_DIR.mkdir(exist_ok=True)

    for key in CATS:
        CATS[key].clear()   # clean for every run

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
