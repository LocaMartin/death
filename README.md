# Telegram Push Notifier

This repository sends a message to a Telegram bot each time a push happens.

## How it works
A GitHub Action runs automatically after every push and executes `send.py`, which sends:

> "hi, it's working"


to the Telegram chat linked to the bot.

## Setup
1. Go to Settings ➜ Secrets ➜ Actions
2. Add two secrets:

| Name       | Value |
|------------|-------|
| BOT_TOKEN  | Your Telegram bot token |
| CHAT_ID    | Your chat ID |

After adding secrets, commit or push anything — you will receive a Telegram notification.

