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
        liquidity = float(pair["liquidity"]["usd"])

        if liquidity < MIN_LIQUIDITY:
            return False

        if liquidity > 5_000_000:
            return False

        return True
    except:
        return False


def is_volume_safe(pair):
    try:
        volume = float(pair["volume"]["h24"])
        liquidity = float(pair["liquidity"]["usd"])

        if volume < MIN_VOLUME_24H:
            return False

        if liquidity == 0:
            return False

        ratio = volume / liquidity

        if ratio > MAX_VOLUME_LIQUIDITY_RATIO:
            return False

        return True
    except:
        return False


def is_price_behavior_safe(pair):
    try:
        price_change = float(pair.get("priceChange", {}).get("h1", 0)) / 100

        # 🚨 big pump = likely dump incoming
        if abs(price_change) > MAX_PRICE_SPIKE:
            return False

        return True
    except:
        return False


def has_activity(pair):
    try:
        volume = float(pair["volume"]["h24"])

        return volume > 1000  # minimal activity
    except:
        return False


def is_valid(pair):
    try:
        if not is_pair_old_enough(pair):
            return False

        if not is_liquidity_safe(pair):
            return False

        if not is_volume_safe(pair):
            return False

        if not is_price_behavior_safe(pair):
            return False

        if not has_activity(pair):
            return False

        return True

    except Exception:
        return False