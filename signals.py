from sniper import calculate_sniper_score
from whale import detect_whale_activity
from db import get_last_entries
from config import MIN_SCORE_FOR_SIGNAL 

def generate_signal(token):
    """
    Generate a buy signal for a memecoin token based on sniper and whale scores.
    
    Returns:
        dict or None: Signal dictionary if criteria met, otherwise None
    """
    symbol = token.get("symbol")
    if not symbol:
        return None

    history = get_last_entries(symbol, limit=10)
    if len(history) < 3:
        return None

    try:
        sniper_score = calculate_sniper_score(token, history)
        whale_score = detect_whale_activity(token, history)
    except Exception as e:
        print(f"Error calculating scores for {symbol}: {e}")
        return None

    total_score = sniper_score + whale_score

    print(f"{symbol} | sniper={sniper_score} | whale={whale_score} | total={total_score}")

    if total_score < getattr(MIN_SCORE_FOR_SIGNAL, "value", 10):
        return None

    entry = token.get("price", 0)
    if entry <= 0:
        return None

    stop_loss = entry * 0.9
    take_profit = entry * 1.7

    return {
        "symbol": symbol,
        "pair_address": token.get("address"), 
        "action": "BUY",
        "price": entry,
        "liquidity": token.get("liquidity", 0),
        "score": total_score,
        "sniper_score": sniper_score,
        "whale_score": whale_score,
        "stop_loss": stop_loss,
        "take_profit": take_profit
    }