import os
import json
import requests

urls = {
    "h1": "https://bbscope.com/static/scope/latest-h1.json",
    "bugc": "https://bbscope.com/static/scope/latest-bc.json",
    "ywh": "https://bbscope.com/static/scope/latest-ywh.json",
    "inti": "https://bbscope.com/static/scope/latest-it.json"
}

mapping = {
    "android": "android",
    "GOOGLE_PLAY_APP_ID": "android",

    "ios": "ios",
    "APPLE_STORE_APP_ID": "ios",
    "TESTFLIGHT": "ios",
    "WINDOWS_APP_STORE_APP_ID": "ios",

    "API": "api",
    "api": "api",

    "HARDWARE": "hardware",
    "Device": "hardware",

    "iot": "iot",

    "CIDR": "ip_address",
    "IP_ADDRESS": "ip_address",
    "IpRange": "ip_address",

    "network": "network",

    "URL": "website",
    "Url": "website",
    "website": "website",
    "web-application": "website",
    "wildcard": "website",
    "WILDCARD": "website",

    "OTHER": "other",
    "other": "other",
    "open-source": "other",
    "AI_MODEL": "other",
    "SMART_CONTRACT": "other",
    "SOURCE_CODE": "other",
    "DOWNLOADABLE_EXECUTABLES": "other",
    "OTHER_APK": "other",
    "OTHER_IPA": "other",
    "application": "other"
}

categories = ["android","api","hardware","ios","iot","ip_address","network","other","website"]

def run_sort():
    log = []

    for platform, url in urls.items():
        platform_dir = f"res/{platform}"
        os.makedirs(platform_dir, exist_ok=True)
        for f in os.listdir(platform_dir):
            os.remove(os.path.join(platform_dir, f))

        log.append(f"\n[*] Sorting: {platform}")
        data = requests.get(url).json()

        results = {c: [] for c in categories}

        for prog in data:
            for asset in prog.get("InScope", []):
                cat = mapping.get(asset.get("Category", "").strip(), None)
                if cat in results:
                    results[cat].append(asset.get("Target", "").strip())

        for cat in categories:
            out_file = os.path.join(platform_dir, f"{cat}.txt")
            unique = sorted(set(results[cat]))
            if unique:
                with open(out_file, "w") as f:
                    f.write("\n".join(unique))
            log.append(f" → Extracted {cat} ({len(unique)} targets)")

        log.append(f"[OK] {platform} completed")

    return "\n".join(log)
