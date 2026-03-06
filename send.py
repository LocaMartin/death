import os
import requests
from lib.sort import run_sort
from lib.extract import merge_targets
from lib.obb import run_obb


def ensure_base_dirs():
    os.makedirs("res", exist_ok=True)
    os.makedirs("out", exist_ok=True)


def send_msg(msg: str):
    BOT_TOKEN = os.getenv("BOT_TOKEN")
    CHAT_ID = os.getenv("CHAT_ID")

    if not BOT_TOKEN or not CHAT_ID:
        raise ValueError("Missing BOT_TOKEN or CHAT_ID environment variables")

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    payload = {
        "chat_id": CHAT_ID,
        "text": msg[:4096]
    }

    requests.post(url, json=payload)


if __name__ == "__main__":
    ensure_base_dirs()

    logs = run_sort()

    for platform in ["h1", "bugc", "ywh", "inti"]:
        msg = logs.get(platform, "")
        if msg.strip():
            send_msg(msg)
            print(f"[SENT] {platform}")
        else:
            print(f"[EMPTY] {platform}")

    merge_log = merge_targets()
    send_msg(merge_log)
    print("[SENT] Merge Log")

    try:
        obb_file = run_obb()
        count = sum(1 for _ in open(obb_file))
        filename = os.path.basename(obb_file)

        send_msg(f"OpenBugBounty updated\nFile: {filename}\nTotal domains: {count}")
        print("[SENT] OBB Update")

    except Exception as e:
        send_msg(f"⚠ OBB error: {e}")
        print(f"[ERROR] OBB — {e}")