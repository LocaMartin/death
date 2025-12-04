# lib/sort.py

import os
import requests

BASE = "res"
os.makedirs(BASE, exist_ok=True)


def ensure_dir(path):
    """Create dir if missing."""
    os.makedirs(path, exist_ok=True)


def sort_platform(name, url, mapping):
    log = [f"[*] Sorting: {name}"]

    ensure_dir(BASE)                                # ensure res/
    platform_dir = f"{BASE}/{name}"
    ensure_dir(platform_dir)                        # ensure /res/platform/

    # Fetch JSON
    try:
        data = requests.get(url, timeout=30).json()
    except Exception as e:
        return f"[ERROR] {name} → Failed to fetch JSON: {e}"

    # result buckets
    results = {v: [] for v in mapping.values()}

    for program in data or []:
        if not isinstance(program, dict):
            continue

        for asset in program.get("InScope", []) or []:
            category = mapping.get(asset.get("Category", "").strip())
            target = asset.get("Target", "").strip()
            if category and target:
                results[category].append(target)

    # delete old files
    for f in os.listdir(platform_dir):
        os.remove(os.path.join(platform_dir, f))

    # save updated files
    for cat, items in results.items():
        file_path = f"{platform_dir}/{cat}.txt"
        unique_items = sorted(set(items))
        with open(file_path, "w") as f:
            f.write("\n".join(unique_items))
        log.append(f" → {cat}.txt : {len(unique_items)} scopes")

    log.append(f"[OK] {name} completed")
    return "\n".join(log)


# ─────────────────────────────────────────────
# PLATFORM-SPECIFIC MAPPINGS
# ─────────────────────────────────────────────

def sort_h1():
    mapping = {
        "AI_MODEL": "ai_model",
        "API": "api",
        "APPLE_STORE_APP_ID": "apple",
        "CIDR": "cidr",
        "DOWNLOADABLE_EXECUTABLES": "exe",
        "GOOGLE_PLAY_APP_ID": "playstore",
        "HARDWARE": "hardware",
        "IP_ADDRESS": "ip",
        "OTHER": "other",
        "OTHER_APK": "apk",
        "OTHER_IPA": "ipa",
        "SMART_CONTRACT": "contract",
        "SOURCE_CODE": "source",
        "TESTFLIGHT": "testflight",
        "URL": "web",
        "WILDCARD": "wildcard",
        "WINDOWS_APP_STORE_APP_ID": "windows"
    }
    return sort_platform("h1", "https://bbscope.com/static/scope/latest-h1.json", mapping)


def sort_bugc():
    mapping = {
        "android": "android",
        "api": "api",
        "hardware": "hardware",
        "ios": "ios",
        "iot": "iot",
        "ip_address": "ip",
        "network": "network",
        "other": "other",
        "website": "website"
    }
    return sort_platform("bugc", "https://bbscope.com/static/scope/latest-bc.json", mapping)


def sort_ywh():
    mapping = {
        "api": "api",
        "application": "app",
        "mobile-application": "mobile",
        "mobile-application-android": "android",
        "mobile-application-ios": "ios",
        "open-source": "source",
        "other": "other",
        "web-application": "web",
        "wildcard": "wildcard"
    }
    return sort_platform("ywh", "https://bbscope.com/static/scope/latest-ywh.json", mapping)


def sort_inti():
    mapping = {
        "Android": "android",
        "Device": "device",
        "IpRange": "cidr",
        "Other": "other",
        "Url": "web",
        "Wildcard": "wildcard",
        "iOS": "ios"
    }
    return sort_platform("inti", "https://bbscope.com/static/scope/latest-it.json", mapping)


# ─────────────────────────────────────────────
# MAIN CONTROLLER USED BY send.py
# ─────────────────────────────────────────────

def run_sort():
    return {
        "h1": sort_h1(),
        "bugc": sort_bugc(),
        "ywh": sort_ywh(),
        "inti": sort_inti(),
    }


if __name__ == "__main__":
    # For standalone testing
    print(sort_h1())
    print(sort_bugc())
    print(sort_ywh())
    print(sort_inti())
