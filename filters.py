# filters.py

import time
from config import (
    MIN_LIQUIDITY,
    MIN_VOLUME_24H,
    MAX_VOLUME_LIQUIDITY_RATIO,
    MAX_PRICE_SPIKE,
    MIN_PAIR_AGE_SECONDS
)

def is_pair_old_enough(pair):
    try:
        created_at = pair.get("pairCreatedAt")
        if not created_at:
            return False
        age_seconds = (time.time() * 1000 - created_at) / 1000
        return age_seconds > MIN_PAIR_AGE_SECONDS
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