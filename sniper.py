# sniper.py
def calculate_sniper_score(token, history):
    score = 0
    liquidity = token["liquidity"]
    volume = token["volume"]
    if liquidity > 10000:
        score += 2
    if liquidity > 30000:
        score += 2
    if len(history) >= 2:
        prev_volume = history[-2][0]
        if volume > prev_volume:
            score += 2
        if prev_volume > 0 and (volume - prev_volume)/prev_volume > 0.5:
            score += 3
    if len(history) >= 2:
        prev_price = history[-2][1]
        if (token["price"] - prev_price)/prev_price < 0.25:
            score += 1
    if 5000 < liquidity < 50000:
        score += 2
    return score

def should_buy(score):
    return score >= 7