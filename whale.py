def detect_whale_activity(token, history):
    """
    Score whale activity based on recent volume spikes, price stability, and liquidity.
    
    Returns:
        int: whale score
    """
    score = 0

    if not history or len(history) < 3:
        return 0

    try:
        volumes = [float(h[0]) for h in history]
        prices = [float(h[1]) for h in history]
    except Exception:
        return 0

    if volumes[-1] > volumes[-2] > volumes[-3]:
        score += 3

    if volumes[-2] > 0:
        spike = (volumes[-1] - volumes[-2]) / volumes[-2]
        if spike > 0.7:
            score += 3

    try:
        price_change = (prices[-1] - prices[-2]) / prices[-2]
        if abs(price_change) < 0.1:
            score += 1
    except Exception:
        pass

    try:
        liquidity = float(token.get("liquidity", 0))
        if liquidity > 20000:
            score += 2
    except Exception:
        pass

    return score