import requests

BOT_TOKEN = "8572714143:AAEcLDZaA-S0rnoyjwB20yfs1sFzT_JSJVQ"
CHAT_ID = "6075833809"
MESSAGE = "hi, it's working"

url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
payload = {"chat_id": CHAT_ID, "text": MESSAGE}

res = requests.post(url, data=payload)
print("Done:", res.text)

