import requests
from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID
from datetime import datetime

def send_signal(signal):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"

        tier_label = "PREMIUM" if signal['score'] >= 2 else "FREE"

        message = (
            f"🚨 MEMECOIN SIGNAL ({tier_label}) 🚨\n\n"
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
            "text": message
        }

        response = requests.post(url, data=payload)

        print(" Telegram response:", response.text)

    except Exception as e:
<<<<<<< HEAD:Telegram_bot.py
        print(" Telegram exception:", e)
=======
        print("Telegram exception:", e)
>>>>>>> c1956ab9a790cbd54d301040b828e0d2f73604d4:telegram_bot.py
