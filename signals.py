from sniper import calculate_sniper_score
from whale import detect_whale_activity
from db import get_last_entries


def generate_signal(token):
    symbol = token["symbol"]

    history = get_last_entries(symbol, limit=10)

    if len(history) < 3:
        return None

    sniper_score = calculate_sniper_score(token, history)
    whale_score = detect_whale_activity(token, history)

    total_score = sniper_score + whale_score

    print(
        f"{symbol} | sniper={sniper_score} | whale={whale_score} | total={total_score}"
    )

    if total_score < 10:
        return None

    entry = token["price"]

    stop_loss = entry * 0.9
    take_profit = entry * 1.7

    return {
        "symbol": symbol,
        "pair_address": token["address"],  # ✅ NEW
        "action": "BUY",
        "price": entry,
        "liquidity": token["liquidity"],
        "score": total_score,
        "sniper_score": sniper_score,
        "whale_score": whale_score,
        "stop_loss": stop_loss,
        "take_profit": take_profit
    }