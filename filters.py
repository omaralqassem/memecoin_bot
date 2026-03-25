from config import MIN_LIQUIDITY, MIN_VOLUME_24H

def is_valid(pair):
    try:
        liquidity = pair["liquidity"]["usd"]
        volume = pair["volume"]["h24"]

        if liquidity is None or volume is None:
            return False

        if liquidity < MIN_LIQUIDITY:
            return False

        if volume < MIN_VOLUME_24H:
            return False

        return True

    except Exception:
        return False