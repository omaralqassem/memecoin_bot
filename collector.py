# collector.py
import requests
from config import DEXSCREENER_URL, BIRDEYE_API
from filters import is_valid
from db import connect_db, insert_token

HEADERS = {"User-Agent": "Mozilla/5.0"}


def fetch_dexscreener_pairs():
    pairs = []
    queries = ["sol", "dog", "inu", "pepe", "cat", "ai"]  # extend as needed

    for q in queries:
        try:
            url = f"{DEXSCREENER_URL}{q}"
            response = requests.get(url, headers=HEADERS, timeout=10)
            response.raise_for_status()
            data = response.json()
            fetched_pairs = data.get("pairs") or []
            print(f"Query '{q}' returned {len(fetched_pairs)} pairs")
            pairs.extend(fetched_pairs)
        except Exception as e:
            print(f"Dexscreener fetch error for '{q}':", e)

    print(f"TOTAL PAIRS FETCHED FROM DEXSCREENER: {len(pairs)}")
    return pairs


def fetch_birdeye_tokens():
    try:
        response = requests.get(BIRDEYE_API, headers=HEADERS, timeout=10)
        response.raise_for_status()
        data = response.json()
        tokens = data.get("tokens") or []
        print(f"Birdeye returned {len(tokens)} tokens")
        return tokens
    except Exception as e:
        print("Birdeye fetch error:", e)
        return []


def extract_token(pair):
    try:
        return {
            "address": pair.get("pairAddress") or pair.get("address"),
            "symbol": pair.get("baseToken", {}).get("symbol") or pair.get("symbol"),
            "name": pair.get("baseToken", {}).get("name") or pair.get("name"),
            "price": float(pair.get("priceUsd", pair.get("price", 0))),
            "volume": float(pair.get("volume", {}).get("h24", pair.get("volume", 0))),
            "liquidity": float(pair.get("liquidity", {}).get("usd", 0)),
        }
    except Exception as e:
        print("Extract error:", e)
        return None


def get_valid_tokens():
    pairs = fetch_dexscreener_pairs()
    pairs.extend(fetch_birdeye_tokens())

    print(f"TOTAL PAIRS BEFORE FILTER: {len(pairs)}")

    tokens = []
    conn = connect_db()
    cursor = conn.cursor()

    for pair in pairs:
        if not is_valid(pair):
            continue

        token = extract_token(pair)
        if not token:
            continue

        # Skip if address is missing
        if not token.get("address"):
            continue

        # Skip if already in DB
        try:
            cursor.execute("SELECT 1 FROM tokens WHERE address=?", (token["address"],))
            if cursor.fetchone():
                continue
        except Exception as e:
            print("DB select error:", e)
            continue

        tokens.append(token)

    conn.close()
    print(f"TOTAL VALID TOKENS AFTER FILTER: {len(tokens)}")
    return tokens