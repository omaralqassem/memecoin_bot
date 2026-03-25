import time
from db import create_table, insert_token
from collector import get_valid_tokens
from signals import generate_signal
from config import INTERVAL
from Telegram_bot import send_signal

def main():
    print(" Starting memecoin signal engine + single Telegram bot")
    create_table()
    seen_tokens = set()
    while True:
        try:
            print("\n Collecting new data...")
            tokens = get_valid_tokens()
            print(f"✅ Found {len(tokens)} tokens")
            for token in tokens:
                insert_token(token)
                signal = generate_signal(token)
                if signal and signal['symbol'] not in seen_tokens:
                    print("\n🚨 SIGNAL DETECTED 🚨")
                    print(signal)
                    send_signal(signal)  
                    seen_tokens.add(signal['symbol'])
            print(f"⏳ Sleeping {INTERVAL} seconds...")
            time.sleep(INTERVAL)
        except Exception as e:
            print(" Pipeline error:", e)
            time.sleep(10)

if __name__ == "__main__":
    main()