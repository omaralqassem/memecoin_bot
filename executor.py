import time
from collector import get_valid_tokens
from signals import generate_signal
from db import insert_token, create_table
from config import INTERVAL

balance = 1000
open_trades = []

MAX_TRADES = 2
MAX_DAILY_LOSS = 0.03

daily_loss = 0


def execute(token):
    global open_trades

    if len(open_trades) >= MAX_TRADES:
        return

    signal = generate_signal(token)

    if not signal:
        return

    open_trades.append(signal)

    print(
        f"🐋 SNIPED: {signal['symbol']} | total={signal['score']} "
        f"(S:{signal['sniper_score']} W:{signal['whale_score']})"
    )


def monitor_trades():
    global balance, daily_loss

    for trade in open_trades[:]:
        current_price = trade["price"]

        entry = trade["price"]

        if current_price > entry * 1.3:
            trade["stop_loss"] = entry * 1.1

        if current_price > entry * 1.6:
            trade["stop_loss"] = entry * 1.3

        if current_price <= trade["stop_loss"]:
            loss = abs(entry - trade["stop_loss"])
            balance -= loss
            daily_loss += loss / 1000
            open_trades.remove(trade)

            print(f"❌ STOP LOSS: {trade['symbol']}")

        elif current_price >= trade["take_profit"]:
            profit = abs(trade["take_profit"] - entry)
            balance += profit
            open_trades.remove(trade)

            print(f"✅ TAKE PROFIT: {trade['symbol']}")


def main():
    global daily_loss

    create_table()

    while True:
        if daily_loss >= MAX_DAILY_LOSS:
            print("🛑 Daily loss limit reached")
            time.sleep(60)
            continue

        tokens = get_valid_tokens()

        for token in tokens:
            insert_token(token)
            execute(token)

        monitor_trades()

        print(f"💰 Balance: {balance:.2f} | Open trades: {len(open_trades)}")

        time.sleep(INTERVAL)


if __name__ == "__main__":
    main()