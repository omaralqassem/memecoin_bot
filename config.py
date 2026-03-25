import os

DEXSCREENER_URL = "https://api.dexscreener.com/latest/dex/search?q=SOL"

MIN_LIQUIDITY = 1000
MIN_VOLUME_24H = 1000

MIN_LIQUIDITY_SIGNAL = 20000
VOLUME_SPIKE_THRESHOLD = 0.5 

INTERVAL = 300  

DB_NAME = "memecoins.db"

TELEGRAM_BOT_TOKEN = os.getenv("8748976085:AAEWdOFj6IcKQRlkkr4q5ggpb_gON2r21Tw")


TELEGRAM_CHAT_ID = os.getenv("memecoinSource")

AI_PREDICT_PERIODS = 6 
AI_PREDICT_FREQ = '5min'