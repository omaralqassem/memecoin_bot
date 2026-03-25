import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
from datetime import datetime
from prophet import Prophet

from config import DB_NAME, AI_PREDICT_PERIODS, AI_PREDICT_FREQ, INTERVAL
from collector import get_valid_tokens
from db import create_table, insert_token
from signals import generate_signal
from telegram_bot import send_signal

from streamlit_autorefresh import st_autorefresh

# ✅ Auto refresh every X seconds
st_autorefresh(interval=INTERVAL * 1000, key="refresh")

st.set_page_config(page_title="Memecoin AI Dashboard", layout="wide")
st.title("🚀 Memecoin AI Dashboard + Bot")

create_table()

# -------------------------
# 🚀 PIPELINE (FIXED)
# -------------------------
def run_pipeline():
    tokens = get_valid_tokens()
    print("TOKENS FOUND:", len(tokens))

    for token in tokens:
        insert_token(token)

        signal = generate_signal(token)
        print("SIGNAL:", signal)

        # ✅ ALWAYS SEND IF SIGNAL EXISTS
        if signal:
            print("SENDING TO TELEGRAM...")
            send_signal(signal)

# ✅ ALWAYS RUN (IMPORTANT FIX)
run_pipeline()

# -------------------------
# 🧪 TEST BUTTON
# -------------------------
if st.button("TEST TELEGRAM"):
    fake_signal = {
        "symbol": "TEST",
        "type": "TEST",
        "price": 1,
        "liquidity": 10000,
        "change_percent": 99,
        "score": 3
    }
    send_signal(fake_signal)
    st.success("Test signal sent!")

# -------------------------
# 📊 DASHBOARD
# -------------------------
conn = sqlite3.connect(DB_NAME)
df = pd.read_sql_query("SELECT * FROM tokens ORDER BY timestamp DESC", conn)
conn.close()

if len(df) > 0:
    df['timestamp'] = pd.to_datetime(df['timestamp'])

    st.subheader("Latest Tokens")
    st.dataframe(df.tail(50))

    top_tokens = df['symbol'].value_counts().head(5).index.tolist()

    st.subheader("Price Trends")
    for token in top_tokens:
        token_df = df[df['symbol'] == token]
        fig = px.line(token_df, x='timestamp', y='price', title=f'{token} Price')
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("Volume Spikes")
    df['prev_volume'] = df.groupby('symbol')['volume'].shift(1)
    df['volume_change'] = (df['volume'] - df['prev_volume']) / df['prev_volume']
    spikes = df[df['volume_change'] > 0.5].tail(20)
    st.dataframe(spikes[['symbol','volume','volume_change','timestamp']])

    st.subheader("AI Predictions")
    for token in top_tokens:
        token_df = df[df['symbol']==token][['timestamp','volume']]
        token_df = token_df.rename(columns={'timestamp':'ds','volume':'y'})

        if len(token_df) < 5:
            continue

        model = Prophet()
        model.fit(token_df)

        future = model.make_future_dataframe(periods=AI_PREDICT_PERIODS, freq=AI_PREDICT_FREQ)
        forecast = model.predict(future)

        fig = px.line(forecast, x='ds', y='yhat', title=f'{token} Prediction')
        st.plotly_chart(fig, use_container_width=True)

else:
    st.warning("No data yet...")
