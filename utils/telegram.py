import requests

# Telegram Bot Credentials
from config import TELEGRAM_BOT_TOKEN,TELEGRAM_CHAT_ID

def send_telegram_message(message):
    """Send trade updates to Telegram"""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    try:
        requests.post(url, json=payload)
    except Exception as e:
        print(f"⚠️ Telegram Error: {e}")
