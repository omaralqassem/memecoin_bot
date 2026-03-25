import requests
from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID
from datetime import datetime

BASE_URL = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"

def send_signal(signal):
    try:
        tier_label = "PREMIUM" if signal['score'] >= 2 else "FREE"

        message = (
            f" 🚨MEMECOIN SIGNAL ({tier_label}) 🚨\n\n"
            f"Symbol: {signal['symbol']}\n"
            f"Type: {signal['type']}\n"
            f"Price: {signal['price']}\n"
            f"Liquidity: {signal['liquidity']}\n"
            f"Change: {signal['change_percent']}%\n"
            f"Score: {signal['score']}\n"
            f"Time: {datetime.utcnow().strftime('%H:%M UTC')}"
        )

        payload = {
            "chat_id": TELEGRAM_CHAT_ID,
            "text": message,
            "parse_mode": "Markdown"
        }

        response = requests.post(BASE_URL, data=payload)
        if response.status_code != 200:
            print("Telegram send error:", response.text)
    except Exception as e:
        print("Telegram exception:", e)