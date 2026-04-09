#settings.py
import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    SOLANA_RPC_URL = os.getenv("SOLANA_RPC_URL")

    TELEGRAM_API_ID = int(os.getenv("TELEGRAM_API_ID"))
    TELEGRAM_API_HASH = os.getenv("TELEGRAM_API_HASH")

settings = Settings()