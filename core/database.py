import sqlite3
import time

class Database:
    def __init__(self, db_path="bot_data.db"):
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row  # Allows accessing columns by name
        self._create_tables()

    def _create_tables(self):
        with self.conn:
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS tokens (
                    mint TEXT PRIMARY KEY,
                    symbol TEXT,
                    rug_score REAL,
                    is_safe INTEGER,
                    created_at INTEGER,
                    tx_count_1m INTEGER DEFAULT 0
                )
            """)
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS hype (
                    mint TEXT,
                    timestamp INTEGER
                )
            """)

    def update_token(self, mint, rug_score, is_safe, tx_count=0):
        with self.conn:
            self.conn.execute("""
                INSERT INTO tokens (mint, rug_score, is_safe, created_at, tx_count_1m)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(mint) DO UPDATE SET
                    rug_score=excluded.rug_score,
                    is_safe=excluded.is_safe,
                    tx_count_1m=excluded.tx_count_1m
            """, (mint, rug_score, 1 if is_safe else 0, int(time.time()), tx_count))

    def add_hype_mention(self, mint_or_symbol):
        with self.conn:
            self.conn.execute("INSERT INTO hype (mint, timestamp) VALUES (?, ?)", 
                             (mint_or_symbol, int(time.time())))

    def get_hype_count(self, mint_or_symbol, window_sec=300):
        cursor = self.conn.cursor()
        now = int(time.time())
        cursor.execute("SELECT COUNT(*) FROM hype WHERE mint = ? AND timestamp > ?", 
                      (mint_or_symbol, now - window_sec))
        return cursor.fetchone()[0]