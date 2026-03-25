import os

DEXSCREENER_URL = "https://api.dexscreener.com/latest/dex/search?q=SOL"

MIN_LIQUIDITY = 1000
MIN_VOLUME_24H = 1000

MIN_LIQUIDITY_SIGNAL = 20000
VOLUME_SPIKE_THRESHOLD = 0.5 

INTERVAL = 300  

DB_NAME = "memecoins.db"

TELEGRAM_BOT_TOKEN = os.getenv("8748976085:AAFVzWuYdaVk9hwUJhsPZhMRE3ZlU0zBoDw")
TELEGRAM_CHAT_ID = os.getenv("memecoinSource")

if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
    raise ValueError(" Telegram config missing! Set TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID")

AI_PREDICT_PERIODS = 6 
AI_PREDICT_FREQ = '5min'
