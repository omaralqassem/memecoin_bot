# db.py
import sqlite3
from config import DB_NAME

def connect_db():
    return sqlite3.connect(DB_NAME)


def create_table():
    conn = connect_db()
    cursor = conn.cursor()

    # Token table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS tokens (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        address TEXT UNIQUE,  -- ensure no duplicates
        symbol TEXT,
        name TEXT,
        price REAL,
        volume REAL,
        liquidity REAL,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # Trades table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS trades (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        symbol TEXT,
        action TEXT,
        price REAL,
        stop_loss REAL,
        take_profit REAL,
        pnl REAL,
        status TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)

    conn.commit()
    conn.close()


def insert_token(token):
    """Insert a new token into the database safely."""
    if not token.get("address"):
        return  # skip tokens without address

    conn = connect_db()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT OR IGNORE INTO tokens (address, symbol, name, price, volume, liquidity)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            token["address"],
            token["symbol"],
            token["name"],
            token["price"],
            token["volume"],
            token["liquidity"]
        ))
        conn.commit()
    except Exception as e:
        print("DB insert error:", e)
    finally:
        conn.close()

def get_last_entries(symbol, limit=10):
    conn = connect_db()
    cursor = conn.cursor()
    rows = []
    try:
        cursor.execute("""
        SELECT volume, price, timestamp
        FROM tokens
        WHERE symbol = ?
        ORDER BY timestamp DESC
        LIMIT ?
        """, (symbol, limit))
        rows = cursor.fetchall()
    except Exception as e:
        print("DB fetch error:", e)
    finally:
        conn.close()
    return rows