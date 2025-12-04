import json
import requests
from lib.sort import run_sort
from lib.extract import merge_targets
# from lib.obb import run_obb

def send_msg(msg: str):
    with open("config.json") as f:
        config = json.load(f)

    BOT_TOKEN = config["BOT_TOKEN"]
    CHAT_ID = config["CHAT_ID"]

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": msg[:4096]}
    requests.post(url, json=payload)


if __name__ == "__main__":
    # STEP 1 — SORT BY PLATFORM
    logs = run_sort()     # returns 4 log blocks

    for platform in ["h1", "bugc", "ywh", "inti"]:
        msg = logs.get(platform, "")
        if msg:
            send_msg(msg)
            print(f"[SENT] {platform}")
        else:
            print(f"[MISSING] {platform}")

    # STEP 2 — OBB CHECK (if you want)
   # obb_log = run_obb()
   # send_msg(obb_log)
   # print("[SENT] OBB Report")

    # STEP 3 — MERGE EXTRACTED TARGETS TO out/
    merge_log = merge_targets()
    send_msg(merge_log)
    print("[SENT] Merge Log")
