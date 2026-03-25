from db import get_last_entries

def calculate_trend(history):
    if len(history) < 3:
        return 0
    
    prices = [h[1] for h in history] 
    return (prices[0] - prices[-1]) / prices[-1]


def calculate_volume_change(history):
    if len(history) < 2:
        return 0
    
    latest = history[0][0]
    prev = history[1][0]
    
    if prev == 0:
        return 0
    
    return (latest - prev) / prev


def generate_signal(token):
    symbol = token["symbol"]
    history = get_last_entries(symbol, limit=5)

    if len(history) < 3:
        return None

    volume_change = calculate_volume_change(history)
    price_trend = calculate_trend(history)
    liquidity = token["liquidity"]

    score = 0

    if volume_change > 0.5:
        score += 2
    elif volume_change > 0.2:
        score += 1

    if price_trend > 0.05:
        score += 2
    elif price_trend > 0:
        score += 1

    if liquidity > 50000:
        score += 2
    elif liquidity > 20000:
        score += 1


    if score >= 5:
        action = "BUY"
    elif score <= 1:
        action = "SELL"
    else:
        action = "HOLD"

    confidence = min(95, score * 15)

    return {
        "symbol": symbol,
        "action": action,
        "confidence": confidence,
        "price": token["price"],
        "liquidity": liquidity,
        "volume_change": round(volume_change * 100, 2),
        "price_trend": round(price_trend * 100, 2),
        "score": score
    }
