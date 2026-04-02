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


def is_liquidity_safe(pair):
    try:
        liquidity = float(pair.get("liquidity", {}).get("usd", 0))
        if liquidity < MIN_LIQUIDITY or liquidity > 5_000_000:
            return False
        return True
    except Exception:
        return False


def is_volume_safe(pair):
    try:
        volume = float(pair.get("volume", {}).get("h24", 0))
        liquidity = float(pair.get("liquidity", {}).get("usd", 0))
        if volume < MIN_VOLUME_24H or liquidity == 0:
            return False
        ratio = volume / liquidity
        if ratio > MAX_VOLUME_LIQUIDITY_RATIO:
            return False
        return True
    except Exception:
        return False


def is_price_behavior_safe(pair):
    try:
        price_change = float(pair.get("priceChange", {}).get("h1", 0)) / 100
        if abs(price_change) > MAX_PRICE_SPIKE:
            return False
        return True
    except Exception:
        return False


def has_activity(pair):
    try:
        volume = float(pair.get("volume", {}).get("h24", 0))
        return volume > 1000
    except Exception:
        return False


def is_valid(pair):
    try:
        return all([
            is_pair_old_enough(pair),
            is_liquidity_safe(pair),
            is_volume_safe(pair),
            is_price_behavior_safe(pair),
            has_activity(pair)
        ])
    except Exception:
        return False