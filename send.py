# send.py

import json
import requests
from lib.sort import run_sort

def send_msg(msg: str):
    with open("config.json") as f:
        config = json.load(f)

    BOT_TOKEN = config["BOT_TOKEN"]
    CHAT_ID = config["CHAT_ID"]

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": msg[:4096]}
    requests.post(url, json=payload)


if __name__ == "__main__":
    logs = run_sort()    # MUST return: {"h1": "...", "bugc": "...", "ywh": "...", "inti": "..."}

    # Send each message separately
    for platform in ["h1", "bugc", "ywh", "inti"]:
        msg = logs.get(platform, "")
        if msg:
            send_msg(msg)
            print(f"[SENT] {platform}")
        else:
            print(f"[MISSING] {platform} log not returned")
