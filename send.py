import json
import requests
from sort import run_sort

def send_msg(msg: str):
    with open("config.json") as f:
        config = json.load(f)

    BOT_TOKEN = config["BOT_TOKEN"]
    CHAT_ID = config["CHAT_ID"]

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    params = {"chat_id": CHAT_ID, "text": msg[:4000]}

    requests.get(url, params=params)

if __name__ == "__main__":
    log = run_sort()   # Run sorting first
    send_msg(log)      # Then send result to Telegram
    print(log)