from db import get_last_entries
from config import VOLUME_SPIKE_THRESHOLD, MIN_LIQUIDITY_SIGNAL

def detect_volume_spike(token):
    symbol = token["symbol"]

    history = get_last_entries(symbol, limit=2)

    if len(history) < 2:
        return None

    latest_volume = history[0][0]
    previous_volume = history[1][0]

    if previous_volume == 0:
        return None

    change = (latest_volume - previous_volume) / previous_volume

    if change > VOLUME_SPIKE_THRESHOLD and token["liquidity"] > MIN_LIQUIDITY_SIGNAL:
        score = 0

        if change > 1.0:
            score += 2
        if token["liquidity"] > 50000:
            score += 1

        return {
            "symbol": symbol,
            "type": "VOLUME_SPIKE",
            "change_percent": round(change * 100, 2),
            "price": token["price"],
            "liquidity": token["liquidity"],
            "score": score
        }

    return None


def generate_signal(token):
    signal = detect_volume_spike(token)

    if signal:
        return signal

    return None