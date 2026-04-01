# executor.py 
import time
import sqlite3
from signals import generate_signal
from config import INTERVAL, MIN_LIQUIDITY, RISK_PER_TRADE, DB_NAME
from telegram_bot import send_signal
from collector import get_valid_tokens

DRY_RUN = True
MAX_OPEN_TRADES = 3
MAX_DAILY_LOSS = 0.05
INITIAL_BALANCE = 1000
balance = INITIAL_BALANCE
daily_loss = 0


def connect_db():
    """Create trades table if not exists and return connection"""
    conn = sqlite3.connect(DB_NAME)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS trades (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol TEXT,
            action TEXT,
            entry_price REAL,
            stop_loss REAL,
            take_profit REAL,
            position_size REAL,
            status TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    return conn


def log_trade(trade):
    """Insert trade record into DB"""
    conn = connect_db()
    conn.execute("""
        INSERT INTO trades (symbol, action, entry_price, stop_loss, take_profit, position_size, status)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        trade['symbol'],
        trade['action'],
        trade['entry_price'],
        trade['stop_loss'],
        trade['take_profit'],
        trade['position_size'],
        trade.get('status', 'OPEN')
    ))
    conn.commit()
    conn.close()


def calculate_position_size(balance, entry_price, stop_loss):
    risk_amount = balance * RISK_PER_TRADE
    return risk_amount / max(abs(entry_price - stop_loss), 1e-6)


def get_live_price(token):
    signal = generate_signal(token)
    return signal['price'] if signal else None


def monitor_trades(open_trades):
    global balance, daily_loss
    for trade in open_trades[:]:
        current_price = get_live_price({'symbol': trade['symbol'], 'liquidity': trade['liquidity']})
        if current_price is None:
            continue

        if current_price <= trade['stop_loss']:
            loss = trade['position_size'] * abs(trade['entry_price'] - trade['stop_loss'])
            balance -= loss
            daily_loss += loss / INITIAL_BALANCE
            trade['status'] = 'STOP_LOSS'
            open_trades.remove(trade)
            print(f"❌ STOP LOSS hit: {trade['symbol']} at {current_price:.6f}")
            send_signal({
                "symbol": trade['symbol'],
                "action": "STOP_LOSS",
                "price": current_price,
                "liquidity": trade['liquidity'],
                "stop_loss": trade['stop_loss'],
                "take_profit": trade['take_profit']
            })
            log_trade(trade)

        elif current_price >= trade['take_profit']:
            profit = trade['position_size'] * abs(trade['take_profit'] - trade['entry_price'])
            balance += profit
            trade['status'] = 'TAKE_PROFIT'
            open_trades.remove(trade)
            print(f"✅ TAKE PROFIT hit: {trade['symbol']} at {current_price:.6f}")
            send_signal({
                "symbol": trade['symbol'],
                "action": "TAKE_PROFIT",
                "price": current_price,
                "liquidity": trade['liquidity'],
                "stop_loss": trade['stop_loss'],
                "take_profit": trade['take_profit']
            })
            log_trade(trade)


def execute_trade(token, open_trades):
    global balance, daily_loss

    if len(open_trades) >= MAX_OPEN_TRADES:
        print(f"⚠️ Max open trades reached, skipping {token['symbol']}")
        return

    signal = generate_signal(token)
    if not signal:
        return

    if signal['liquidity'] < MIN_LIQUIDITY_SIGNAL:
        print(f"⚠️ Skipping {token['symbol']}, low liquidity")
        return

    if daily_loss >= MAX_DAILY_LOSS:
        print("⚠️ Daily loss limit reached, no new trades allowed")
        return

    position_size = calculate_position_size(balance, signal['price'], signal['stop_loss'])
    trade = {
        'symbol': token['symbol'],
        'action': 'BUY',
        'entry_price': signal['price'],
        'stop_loss': signal['stop_loss'],
        'take_profit': signal['take_profit'],
        'position_size': position_size,
        'liquidity': signal['liquidity']
    }

    open_trades.append(trade)
    print(f"🟢 Trade executed: {trade['symbol']} @ {trade['entry_price']:.6f} | size={position_size:.4f}")

    if not DRY_RUN:
        send_signal(trade)
        log_trade(trade)
import sqlite3
from config import DB_NAME

conn = sqlite3.connect(DB_NAME)
conn.execute("""
CREATE TABLE IF NOT EXISTS tokens (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    symbol TEXT,
    name TEXT,
    price REAL,
    volume REAL,
    liquidity REAL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
)
""")
conn.execute("""
CREATE TABLE IF NOT EXISTS trades (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    symbol TEXT,
    action TEXT,
    entry_price REAL,
    stop_loss REAL,
    take_profit REAL,
    position_size REAL,
    status TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
)
""")
conn.commit()
conn.close()

def main():
    open_trades = []

    while True:
        try:
            print("🔄 Fetching valid tokens...")
            tokens = get_valid_tokens()
            print(f"✅ {len(tokens)} tokens fetched")

            for token in tokens:
                execute_trade(token, open_trades)

            monitor_trades(open_trades)
            print(f"💰 Balance: {balance:.2f} | Open trades: {len(open_trades)}")
            time.sleep(INTERVAL)

        except Exception as e:
            print("⚠️ Executor error:", e)
            time.sleep(10)


if __name__ == "__main__":
    main()