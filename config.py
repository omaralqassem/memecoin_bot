import streamlit as st


BIRDEYE_API = "https://public-api.birdeye.so/defi/tokenlist"

DEXSCREENER_URL = "https://api.dexscreener.com/latest/dex/search?q="

HELIUS_API_KEY = st.secrets.get("HELIUS_API_KEY", "")
HELIUS_API_URL = f"https://api.helius.xyz/v0/addresses/transactions?api-key={HELIUS_API_KEY}" if HELIUS_API_KEY else None


MIN_LIQUIDITY = 8000               
MIN_VOLUME_24H = 2000              
MAX_VOLUME_LIQUIDITY_RATIO = 20     
MAX_PRICE_SPIKE = 3                 
MIN_PAIR_AGE_SECONDS = 30           

INTERVAL = 5                     
DB_NAME = "memecoins.db"

INITIAL_BALANCE = 1000
RISK_PER_TRADE = 0.01           
MAX_DAILY_LOSS = 0.05          
SLIPPAGE = 0.01                
FEE = 0.003                         
MIN_LIQUIDITY_SIGNAL = 15000         
MIN_SCORE_FOR_SIGNAL = 10         


TELEGRAM_BOT_TOKEN = st.secrets.get("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = st.secrets.get("TELEGRAM_CHAT_ID", "")

AI_PREDICT_PERIODS = 10
AI_PREDICT_FREQ = "min"