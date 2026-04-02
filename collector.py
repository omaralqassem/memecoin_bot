import requests
from config import DEXSCREENER_URL
from filters import is_valid
from db import connect_db

HEADERS = {"User-Agent": "Mozilla/5.0"}


def fetch_pairs():
    try:
        response = requests.get(DEXSCREENER_URL, headers=HEADERS, timeout=10)
        response.raise_for_status()
        data = response.json()

        pairs = data.get("pairs", [])
        print(f"TOTAL PAIRS: {len(pairs)}")

        return pairs
    except Exception as e:
        print("Fetch error:", e)
        return []


def fetch_price(pair_address):
    try:
        url = f"https://api.dexscreener.com/latest/dex/pairs/solana/{pair_address}"
        response = requests.get(url, headers=HEADERS, timeout=5)
        response.raise_for_status()

        data = response.json()
        pairs = data.get("pairs", [])

        if not pairs:
            return None

        return float(pairs[0]["priceUsd"])
    except Exception as e:
        print("Price fetch error:", e)
        return None


def extract_token(pair):
    try:
        return {
            "address": pair.get("pairAddress"),
            "symbol": pair["baseToken"]["symbol"],
            "name": pair["baseToken"]["name"],
            "price": float(pair["priceUsd"]),
            "volume": float(pair["volume"]["h24"]),
            "liquidity": float(pair["liquidity"]["usd"]),
        }
    except Exception as e:
        print("Extract error:", e)
        return None


def get_valid_tokens():
    pairs = fetch_pairs()
    tokens = []

    conn = connect_db()
    cursor = conn.cursor()

    for pair in pairs:
        if not is_valid(pair):
            continue

        token = extract_token(pair)
        if not token:
            continue

        # Avoid duplicates
        cursor.execute(
            "SELECT 1 FROM tokens WHERE address=?",
            (token["address"],)
        )

        if cursor.fetchone():
            continue

        print(f"VALID TOKEN: {token['symbol']} | LQ={token['liquidity']}")

        tokens.append(token)

    conn.close()
    print(f"TOTAL VALID TOKENS: {len(tokens)}")
    return tokens