import os
import json
import requests

urls = {
    "h1": "https://bbscope.com/static/scope/latest-h1.json",
    "bugc": "https://bbscope.com/static/scope/latest-bc.json",
    "ywh": "https://bbscope.com/static/scope/latest-ywh.json",
    "inti": "https://bbscope.com/static/scope/latest-it.json"
}

categories = [
    "android", "api", "hardware", "ios", "iot",
    "ip_address", "network", "other", "website"
]

def run_sort():
    log = []

    for platform, url in urls.items():
        platform_dir = f"res/{platform}"
        os.makedirs(platform_dir, exist_ok=True)

        for file in os.listdir(platform_dir):
            os.remove(os.path.join(platform_dir, file))

        log.append(f"\n[*] Sorting: {platform}")

        data = requests.get(url).json()

        for category in categories:
            out_file = os.path.join(platform_dir, f"{category}.txt")
            results = []

            for prog in data:
                if prog.get("InScope"):
                    for entry in prog["InScope"]:
                        if entry.get("Category") == category:
                            results.append(entry.get("Target", "").strip())

            if results:
                results = sorted(list(set(results)))
                with open(out_file, "w") as f:
                    f.write("\n".join(results))

            log.append(f" → Extracted {category} ({len(results)} targets)")

        log.append(f"[OK] {platform} completed")

    return "\n".join(log)
