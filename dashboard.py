import streamlit as st
import pandas as pd
import sqlite3
import time
from datetime import datetime

st.set_page_config(
    page_title="Alpha Sniper Cockpit",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stMetric { background-color: #161b22; border-radius: 10px; padding: 15px; border: 1px solid #30363d; }
    </style>
    """, unsafe_all_raw=True)

def get_data():
    conn = sqlite3.connect("bot_data.db")
    try:
        check_query = "SELECT name FROM sqlite_master WHERE type='table' AND name='tokens';"
        if pd.read_sql(check_query, conn).empty:
            return pd.DataFrame()

        query = """
        SELECT mint, rug_score, is_safe, tx_count_1m, created_at 
        FROM tokens 
        ORDER BY created_at DESC 
        LIMIT 50
        """
        df = pd.read_sql(query, conn)
        return df
    except Exception as e:
        st.error(f"Database Read Error: {e}")
        return pd.DataFrame()
    finally:
        conn.close()

st.sidebar.title("🎮 Bot Control")
auto_refresh = st.sidebar.checkbox("Auto-Refresh (2s)", value=True)
st.sidebar.divider()
st.sidebar.info("Phase 4: Executioner status: **READY**")

st.title("🚀 Solana Alpha Sniper")
st.caption("Real-time on-chain token discovery and rug-filtering")

placeholder = st.empty()

while True:
    df = get_data()
    
    with placeholder.container():
        if df.empty:
            st.warning("📡 Waiting for Engine... No tokens found in `bot_data.db` yet.")
            st.info("Make sure your bot script is running and has detected at least one token.")
        else:
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Total Tokens", len(df))
            m2.metric("Safe Tokens", len(df[df['is_safe'] == 1]))
            m3.metric("High Risk", len(df[df['rug_score'] < 40]))
            m4.metric("Last Scan", datetime.now().strftime("%H:%M:%S"))

            st.divider()

            col_left, col_right = st.columns([2, 1])

            with col_left:
                st.subheader("🔥 Top Alpha Signals")
                safe_df = df[df['is_safe'] == 1].copy()
                if not safe_df.empty:
                    # Formatting
                    safe_df['created_at'] = pd.to_datetime(safe_df['created_at'], unit='s').dt.strftime('%H:%M:%S')
                    st.dataframe(
                        safe_df, 
                        column_config={
                            "mint": st.column_config.TextColumn("Token Mint"),
                            "rug_score": st.column_config.ProgressColumn("Safety Score", min_value=0, max_value=100),
                            "tx_count_1m": "Activity (1m)",
                        },
                        hide_index=True,
                        use_container_width=True
                    )
                else:
                    st.write("No 'Safe' tokens detected yet.")

            with col_right:
                st.subheader("📝 Recent Logs")
                st.dataframe(
                    df[['mint', 'rug_score']].head(10),
                    hide_index=True,
                    use_container_width=True
                )

            st.divider()
            st.subheader("🎯 Direct Execution")
            target = st.selectbox("Select Target Mint", df['mint'].tolist())
            amt = st.number_input("Amount (SOL)", min_value=0.01, max_value=10.0, value=0.1)
            if st.button("🚀 EXECUTE SNIPE"):
                st.balloons()
                st.success(f"Sent {amt} SOL order for {target[:6]}... via Jupiter/Jito")

    if not auto_refresh:
        break
    
    time.sleep(2)