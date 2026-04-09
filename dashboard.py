import streamlit as st
import pandas as pd
import sqlite3
import time

# Set page to wide mode for a professional "Terminal" look
st.set_page_config(page_title="Alpha Sniper Dashboard", layout="wide")

def get_data():
    conn = sqlite3.connect("bot_data.db")
    # Fetch the latest 20 tokens that passed the rug filter
    query = """
    SELECT mint, symbol, rug_score, tx_count_1m, created_at 
    FROM tokens 
    WHERE is_safe = 1 
    ORDER BY created_at DESC 
    LIMIT 20
    """
    df = pd.read_sql(query, conn)
    conn.close()
    return df

st.title("🚀 Solana Alpha Sniper")
st.subheader("Live Secure Token Feed")

# Create a placeholder so we can refresh the table without reloading the whole page
placeholder = st.empty()

while True:
    with placeholder.container():
        data = get_data()
        
        if not data.empty:
            # Formatting the display
            data['created_at'] = pd.to_datetime(data['created_at'], unit='s')
            
            # Display Metrics
            col1, col2, col3 = st.columns(3)
            col1.metric("Active Signals", len(data))
            col2.metric("Avg Rug Score", round(data['rug_score'].mean(), 2))
            col3.metric("Last Update", time.strftime("%H:%M:%S"))

            # The Main Table
            st.dataframe(data, use_container_width=True)
            
            # Add a button for "Manual Buy" (We'll link this in Phase 4)
            selected_mint = st.selectbox("Select Mint to Snipe", data['mint'].tolist())
            if st.button(f"🚀 Snipe {selected_mint[:6]}..."):
                st.warning("Phase 4 Execution Engine required for live trades!")
        else:
            st.info("Waiting for the engine to find safe tokens...")

    time.sleep(2) # Refresh every 2 seconds