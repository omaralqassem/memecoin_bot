#signals.py
import pandas as pd
from risk import calculate_levels

def compute_indicators(history):
    if len(history) < 10:
        return None

    df = pd.DataFrame(history, columns=["volume", "price", "timestamp"])
    df = df[::-1] 

    # EMA (trend)
    df["ema"] = df["price"].ewm(span=5).mean()

    # RSI
    delta = df["price"].diff()
    gain = (delta.where(delta > 0, 0)).rolling(5).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(5).mean()

    rs = gain / loss
    df["rsi"] = 100 - (100 / (1 + rs))

    return df


def generate_signal(token, history=None):
 
    symbol = token["symbol"]

    if history is None:
        from db import get_last_entries
        history = get_last_entries(symbol, limit=15)

    if len(history) < 10:
        return None

    df = compute_indicators(history)
    if df is None:
        return None

    latest = df.iloc[-1]
    prev = df.iloc[-2]

    price = latest["price"]
    ema = latest["ema"]
    rsi = latest["rsi"]

    volume_now = latest["volume"]
    volume_prev = prev["volume"]

    liquidity = token["liquidity"]

    trend_up = price > ema
    healthy_rsi = 50 < rsi < 70
    volume_increasing = volume_now > volume_prev
    price_jump = (price - prev["price"]) / prev["price"]
    not_pumped = price_jump < 0.15  

    if not (trend_up and healthy_rsi and volume_increasing and not_pumped):
        return None

    stop_loss, take_profit = calculate_levels(price)

    return {
        "symbol": symbol,
        "action": "BUY",
        "price": price,
        "liquidity": liquidity,
        "rsi": round(rsi, 2),
        "ema": round(ema, 6),
        "volume": volume_now,
        "stop_loss": stop_loss,
        "take_profit": take_profit
    }