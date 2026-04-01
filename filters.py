# filters.py
from config import (
    MIN_LIQUIDITY,
    MIN_VOLUME_24H,
    MAX_VOLUME_LIQUIDITY_RATIO,
    MAX_PRICE_SPIKE
)
import time

MIN_PAIR_AGE_SECONDS = 300  

def is_pair_old_enough(pair):
    """Check if the pair has existed long enough"""
    try:
        created_at = pair.get("pairCreatedAt")
        if not created_at:
            return False
        age = (time.time() * 1000 - created_at) / 1000
        return age > MIN_PAIR_AGE_SECONDS
    except Exception:
        return False

def is_valid(pair):
    try:
        liquidity = float(pair["liquidity"]["usd"])
        volume = float(pair["volume"]["h24"])
        price_change = float(pair.get("priceChange", {}).get("h1", 0)) / 100

        if not is_pair_old_enough(pair):
            return False

        if liquidity < MIN_LIQUIDITY:
            return False

        if volume < MIN_VOLUME_24H:
            return False

        if liquidity > 0:
            ratio = volume / liquidity
            if ratio > MAX_VOLUME_LIQUIDITY_RATIO:
                return False

        if abs(price_change) > MAX_PRICE_SPIKE:
            return False

        return True

    except Exception:
        return False