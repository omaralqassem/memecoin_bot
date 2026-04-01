# collector.py 
import requests
import time
from config import DEXSCREENER_URL
from filters import is_valid
from db import insert_token, connect_db

HEADERS = {"User-Agent": "Mozilla/5.0"}

def fetch_pairs(retries=3):
    for attempt in range(retries):
        try:
            response = requests.get(DEXSCREENER_URL, headers=HEADERS, timeout=30)
            response.raise_for_status()
            data = response.json()
            pairs = data.get("pairs", [])
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
    conn = connect_db()
    cursor = conn.cursor()

    for pair in pairs:
        if is_valid(pair):
            token = extract_token(pair)
            if token:
                cursor.execute("SELECT 1 FROM tokens WHERE symbol=? ORDER BY timestamp DESC LIMIT 1", (token["symbol"],))
                if cursor.fetchone():
                    continue
                valid_tokens.append(token)
                insert_token(token)

    conn.close()
    return valid_tokens