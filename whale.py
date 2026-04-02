# whale.py

def detect_whale_activity(token, history):
    score = 0

    if len(history) < 3:
        return 0

    volumes = [h[0] for h in history]
    prices = [h[1] for h in history]

    if volumes[-1] > volumes[-2] > volumes[-3]:
        score += 3

    if volumes[-2] > 0:
        spike = (volumes[-1] - volumes[-2]) / volumes[-2]
        if spike > 0.7:
            score += 3

    price_change = (prices[-1] - prices[-2]) / prices[-2]
    if abs(price_change) < 0.1:
        score += 1

    liquidity = token["liquidity"]
    if liquidity > 20000:
        score += 2

    return score