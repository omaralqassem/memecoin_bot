import streamlit as st
import pandas as pd
import sqlite3
import time
from datetime import datetime

st.set_page_config(page_title="Alpha Sniper Advisor", layout="wide")

def get_data():
    conn = sqlite3.connect("bot_data.db")
    try:
        if pd.read_sql("SELECT name FROM sqlite_master WHERE name='tokens'", conn).empty:
            return pd.DataFrame()
        df = pd.read_sql("SELECT * FROM tokens ORDER BY created_at DESC LIMIT 40", conn)
        return df
    except: return pd.DataFrame()
    finally: conn.close()

st.title("🚀 Solana Alpha Advisor")
st.subheader("Manual Trading Signal Feed")

placeholder = st.empty()

while True:
    df = get_data()
    with placeholder.container():
        if df.empty:
            st.info("📡 Scanning blockchain... No signals yet.")
        else:
            safe_tokens = df[df['is_safe'] == 1]
            c1, c2 = st.columns(2)
            c1.metric("Signals Found", len(safe_tokens))
            c2.metric("Last Scan", datetime.now().strftime("%H:%M:%S"))

            st.markdown("### 🔥 Verified Signals (Click Link to Buy)")
            if not safe_tokens.empty:
                display_df = safe_tokens.copy()
                display_df['Chart'] = display_df['mint'].apply(lambda x: f"https://dexscreener.com/solana/{x}")
                
                st.dataframe(
                    display_df[['mint', 'rug_score', 'Chart']],
                    column_config={
                        "mint": "Token Address",
                        "rug_score": st.column_config.ProgressColumn("Safety Score", min_value=0, max_value=100),
                        "Chart": st.column_config.LinkColumn("DexScreener Link")
                    },
                    use_container_width=True,
                    hide_index=True
                )
            else:
                st.write("No safe tokens found in the last batch.")

            with st.expander("📝 Full Audit Logs (Including Rejected Tokens)"):
                st.table(df[['mint', 'rug_score', 'is_safe']].head(10))

    time.sleep(2)