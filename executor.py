import time
from collector import get_valid_tokens, fetch_price  # ✅ UPDATED
from signals import generate_signal
from db import insert_token, create_table
from config import INTERVAL
from config import FEE, SLIPPAGE
from collector import fetch_price
balance = 1000
open_trades = []

MAX_TRADES = 2
MAX_DAILY_LOSS = 0.03

daily_loss = 0


from risk import calculate_position_size

def execute(token):
    global open_trades, balance

    if len(open_trades) >= MAX_TRADES:
        return

    signal = generate_signal(token)

    if not signal:
        return

    entry = signal["price"]
    stop_loss = signal["stop_loss"]

    position_size = calculate_position_size(balance, entry, stop_loss)

    if position_size <= 0:
        return

    signal["size"] = position_size

    open_trades.append(signal)

    print(
        f"🐋 SNIPED: {signal['symbol']} | size={position_size:.2f} | "
        f"entry={entry} | SL={stop_loss}"
    )


def monitor_trades():
    global balance, daily_loss

    for trade in open_trades[:]:
        entry = trade["price"]
        size = trade["size"]

        current_price = fetch_price(trade["pair_address"])

        if not current_price:
            continue

        effective_price = current_price * (1 - SLIPPAGE)

        print(f"{trade['symbol']} | entry={entry} | current={effective_price}")

        if effective_price > entry * 1.3:
            trade["stop_loss"] = entry * 1.1

        if effective_price > entry * 1.6:
            trade["stop_loss"] = entry * 1.3

        if effective_price <= trade["stop_loss"]:
            pnl = (trade["stop_loss"] - entry) * size

            pnl -= abs(entry * size) * FEE

            balance += pnl
            daily_loss += abs(pnl) / balance

            open_trades.remove(trade)

            print(f"❌ STOP LOSS: {trade['symbol']} | PnL={pnl:.2f}")

        elif effective_price >= trade["take_profit"]:
            pnl = (trade["take_profit"] - entry) * size

            pnl -= abs(entry * size) * FEE

            balance += pnl

            open_trades.remove(trade)

            print(f"✅ TAKE PROFIT: {trade['symbol']} | PnL={pnl:.2f}")
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