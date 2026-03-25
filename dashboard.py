import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
from datetime import datetime
from prophet import Prophet

from config import (
    DB_NAME, AI_PREDICT_PERIODS, AI_PREDICT_FREQ, INTERVAL
)
from collector import get_valid_tokens
from db import create_table, insert_token
from signals import generate_signal
from telegram_bot import send_signal
from streamlit_autorefresh import st_autorefresh

st_autorefresh(interval=INTERVAL * 1000, key="collector_refresh")

st.set_page_config(page_title="Memecoin AI Dashboard", layout="wide")
st.title("🚀 Memecoin AI Dashboard + Telegram Bot")

create_table()

if 'last_run' not in st.session_state:
    st.session_state.last_run = None

if 'seen_tokens' not in st.session_state:
    st.session_state.seen_tokens = set()

def run_pipeline():
    tokens = get_valid_tokens()
    st.write(f"Fetched {len(tokens)} tokens")

    for token in tokens:
        insert_token(token)

        signal = generate_signal(token)

        if signal and signal['symbol'] not in st.session_state.seen_tokens:
            st.success(f"🚨 SIGNAL DETECTED: {signal}")

            send_signal(signal)

            st.session_state.seen_tokens.add(signal['symbol'])

    st.session_state.last_run = datetime.utcnow()


if st.session_state.last_run is None:
    run_pipeline()

if st.button("Run Collector Now"):
    run_pipeline()

if st.button("TEST TELEGRAM"):
    test_signal = {
        "symbol": "TEST",
        "action": "BUY",
        "confidence": 80,
        "price": 1,
        "liquidity": 10000,
        "volume_change": 120,
        "price_trend": 10,
        "score": 5
    }

    st.write("Sending test signal:", test_signal)

    send_signal(test_signal)

    st.success("Test message sent!")
st.write(f"Last collector run: {st.session_state.last_run}")

conn = sqlite3.connect(DB_NAME)
df = pd.read_sql_query("SELECT * FROM tokens ORDER BY timestamp DESC", conn)
conn.close()

df['timestamp'] = pd.to_datetime(df['timestamp'])

st.subheader("📋 Latest Tokens")
st.dataframe(df.tail(50))

top_tokens = df['symbol'].value_counts().head(5).index.tolist()

st.subheader("📈 Price Trend of Top Tokens")
for token in top_tokens:
    token_df = df[df['symbol'] == token]

    fig = px.line(
        token_df,
        x='timestamp',
        y='price',
        title=f'{token} Price Trend'
    )
    st.plotly_chart(fig, use_container_width=True)

st.subheader(" Volume Spike Alerts")

df['prev_volume'] = df.groupby('symbol')['volume'].shift(1)
df['volume_change'] = (df['volume'] - df['prev_volume']) / df['prev_volume']

volume_spikes = df[df['volume_change'] > 0.5].tail(20)

st.dataframe(
    volume_spikes[
        ['symbol', 'price', 'liquidity', 'volume', 'volume_change', 'timestamp']
    ]
)

st.subheader("🤖 AI-Based Volume Prediction")

for token in top_tokens:
    token_df = df[df['symbol'] == token][['timestamp', 'volume']]

    token_df = token_df.rename(columns={
        'timestamp': 'ds',
        'volume': 'y'
    })

    if len(token_df) < 5:
        continue

    try:
        model = Prophet(
            daily_seasonality=False,
            weekly_seasonality=False,
            yearly_seasonality=False
        )

        model.fit(token_df)

        future = model.make_future_dataframe(
            periods=AI_PREDICT_PERIODS,
            freq=AI_PREDICT_FREQ
        )

        forecast = model.predict(future)

        fig = px.line(
            forecast,
            x='ds',
            y='yhat',
            title=f'{token} Volume Prediction'
        )

        st.plotly_chart(fig, use_container_width=True)

    except Exception as e:
        st.warning(f"Prediction failed for {token}: {e}")
