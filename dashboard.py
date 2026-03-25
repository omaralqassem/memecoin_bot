import streamlit as st
from streamlit_autorefresh import st_autorefresh
import sqlite3
import pandas as pd

from collector import get_valid_tokens
from db import create_table, insert_token
from signals import generate_signal
from telegram_bot import send_signal
from config import INTERVAL, DB_NAME

st.set_page_config(page_title="Memecoin Bot", layout="wide")

# 🔄 Auto refresh
st_autorefresh(interval=INTERVAL * 1000, key="refresh")

st.title("🚀 Memecoin Signal Bot")

create_table()

# 🧠 Prevent duplicate spam
if "seen_tokens" not in st.session_state:
    st.session_state.seen_tokens = set()


def run_pipeline():
    tokens = get_valid_tokens()
    st.write(f"Fetched tokens: {len(tokens)}")

    for token in tokens:
        insert_token(token)

        signal = generate_signal(token)

        if signal and signal['symbol'] not in st.session_state.seen_tokens:
            st.success(f"🚨 SIGNAL: {signal}")

            send_signal(signal)

            st.session_state.seen_tokens.add(signal['symbol'])


run_pipeline()

# 🧪 Manual test button
if st.button("TEST TELEGRAM"):
    send_signal({
        "symbol": "TEST",
        "type": "TEST",
        "price": 1,
        "liquidity": 10000,
        "change_percent": 99,
        "score": 3
    })
    st.success("Test triggered!")

# 📊 Show DB
conn = sqlite3.connect(DB_NAME)
df = pd.read_sql_query("SELECT * FROM tokens", conn)
conn.close()

st.dataframe(df.tail(50))