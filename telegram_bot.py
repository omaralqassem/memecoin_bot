#telegram_bot.py
import requests
from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID
from datetime import datetime
import streamlit as st

def send_signal(signal):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"

        emoji = {
            "BUY": "🟢",
            "SELL": "🔴",
            "HOLD": "⚖️"
        }
        message = (
            f"🟢 BUY SIGNAL\n"
            f"Symbol: {signal['symbol']}\n"
            f"Price: {signal['price']}\n"
            f"Liquidity: ${signal['liquidity']}\n"
            f"Stop Loss: {signal['stop_loss']}\n"
            f"Take Profit: {signal['take_profit']}\n"
        )

        payload = {
            "chat_id": TELEGRAM_CHAT_ID,
            "text": message,
            "parse_mode": "Markdown"
        }

        response = requests.post(url, data=payload)
        print("Telegram:", response.text)

    except Exception as e:
        print("Telegram error:", e)