import requests
import time
from config import DEXSCREENER_URL
from filters import is_valid

HEADERS = {"User-Agent": "Mozilla/5.0"}

def fetch_pairs(retries=3):
    for attempt in range(retries):
        try:
            print(f"Fetching data... attempt {attempt+1}")
            response = requests.get(
                DEXSCREENER_URL, headers=HEADERS, timeout=30
            )
            response.raise_for_status()
            data = response.json()
            pairs = data.get("pairs", [])
            print(f"Fetched {len(pairs)} pairs")
            return pairs
        except Exception as e:
            print("Error fetching data:", e)
            if attempt < retries - 1:
                time.sleep(2)
            else:
                return []

def extract_token(pair):
    try:
        return {
            "symbol": pair["baseToken"]["symbol"],
            "name": pair["baseToken"]["name"],
            "price": float(pair["priceUsd"]),
            "volume": float(pair["volume"]["h24"]),
            "liquidity": float(pair["liquidity"]["usd"]),
        }
    except Exception:
        return None

def get_valid_tokens():
    pairs = fetch_pairs()
    valid_tokens = []
    for pair in pairs:
        if is_valid(pair):
            token = extract_token(pair)
            if token:
                valid_tokens.append(token)
    return valid_tokens