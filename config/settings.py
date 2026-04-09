import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    SOLANA_RPC_URL = os.getenv("SOLANA_RPC_URL", "https://api.mainnet-beta.solana.com")

    TELEGRAM_API_ID = int(os.getenv("TELEGRAM_API_ID", 0))
    TELEGRAM_API_HASH = os.getenv("TELEGRAM_API_HASH", "")


    ML_CONFIDENCE_THRESHOLD = float(os.getenv("ML_CONFIDENCE_THRESHOLD", 0.80))
    MIN_SAFE_SCORE = int(os.getenv("MIN_SAFE_SCORE", 60))
    
    HYPE_DELAY_SECONDS = 15 

settings = Settings()