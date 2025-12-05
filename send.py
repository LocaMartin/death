# send.py

import os
import json
import requests
from lib.sort import run_sort
from lib.extract import merge_targets
from lib.obb import run_obb

'''
from scripts.nxc import
from scripts.ad import
from scripts.dns import
from scripts.header import
from scripts.nxc import
from scripts.telehub import
'''

def ensure_base_dirs():
    os.makedirs("res", exist_ok=True)
    os.makedirs("out", exist_ok=True)

def send_msg(msg: str):
    with open("config.json") as f:
        config = json.load(f)

    BOT_TOKEN = config["BOT_TOKEN"]
    CHAT_ID = config["CHAT_ID"]

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": msg[:4096]}
    requests.post(url, json=payload)


if __name__ == "__main__":
    ensure_base_dirs()

    logs = run_sort()  # returns logs for each platform

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
        obb_file = run_obb()  # returns file path
        count = sum(1 for _ in open(obb_file))
        filename = os.path.basename(obb_file)

        send_msg(f"OpenBugBounty updated\nFile: {filename}\nTotal domains: {count}")
        print("[SENT] OBB Update")

    except Exception as e:
        send_msg(f"⚠ OBB error: {e}")
        print(f"[ERROR] OBB — {e}")