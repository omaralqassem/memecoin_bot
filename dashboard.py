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

st_autorefresh(interval=INTERVAL * 1000, key="refresh")

st.title("🚀 Memecoin Signal Bot")

create_table()


def run_pipeline():
    tokens = get_valid_tokens()
    print("TOKENS:", len(tokens))

    for token in tokens:
        insert_token(token)

        signal = generate_signal(token)
        print("SIGNAL:", signal)

        if signal:
            print("🚀 Sending signal...")
            send_signal(signal)

run_pipeline()


if st.button("TEST TELEGRAM"):
    send_signal({
        "symbol": "TEST",
        "type": "TEST",
        "price": 1,
        "liquidity": 10000,
        "change_percent": 99,
        "score": 3
    })
    st.success("Test sent!")


conn = sqlite3.connect(DB_NAME)
df = pd.read_sql_query("SELECT * FROM tokens", conn)
conn.close()

st.dataframe(df.tail(50))