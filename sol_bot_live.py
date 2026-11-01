
import streamlit as st
import requests
import time
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="SOL Live Trader", page_icon="🚀", layout="wide")

st.title("🚀 SOL Live Trader - Real Time")
st.markdown("Live Solana price tracking bot")

# Sidebar
st.sidebar.header("Settings")
auto_refresh = st.sidebar.checkbox("Auto Refresh (5 sec)", value=True)
buy_threshold = st.sidebar.number_input("Buy Alert Below $", value=140.0)
sell_threshold = st.sidebar.number_input("Sell Alert Above $", value=200.0)

def get_sol_price():
    try:
        # CoinGecko API - free
        url = "https://api.coingecko.com/api/v3/simple/price?ids=solana&vs_currencies=usd&include_24hr_change=true"
        r = requests.get(url, timeout=10)
        data = r.json()
        price = data['solana']['usd']
        change = data['solana'].get('usd_24h_change', 0)
        return price, change
    except:
        return None, None

def get_chart_data():
    try:
        url = "https://api.coingecko.com/api/v3/coins/solana/market_chart?vs_currency=usd&days=1"
        r = requests.get(url, timeout=10)
        prices = r.json()['prices']
        df = pd.DataFrame(prices, columns=['timestamp', 'price'])
        df['time'] = pd.to_datetime(df['timestamp'], unit='ms')
        return df
    except:
        return None

# Main display
col1, col2, col3 = st.columns(3)

price, change = get_sol_price()

if price:
    with col1:
        st.metric("SOL Price", f"${price:.2f}", f"{change:.2f}%")
    with col2:
        st.write(f"**Last Update:** {datetime.now().strftime('%H:%M:%S')}")
        if price <= buy_threshold:
            st.success(f"🟢 BUY SIGNAL! Price below ${buy_threshold}")
        elif price >= sell_threshold:
            st.error(f"🔴 SELL SIGNAL! Price above ${sell_threshold}")
        else:
            st.info("⚪ HOLD - Waiting for signal")
    with col3:
        st.write(f"**Status:** 🟢 LIVE")

    # Chart
    st.subheader("24h Chart")
    df = get_chart_data()
    if df is not None:
        st.line_chart(df.set_index('time')['price'])
    else:
        st.write("Loading chart...")

    # Trade log
    st.subheader("Live Log")
    st.code(f"[{datetime.now()}] SOL: ${price} | Change: {change:.2f}% | Bot: Monitoring...")
    
else:
    st.error("Failed to fetch price. API limit - wait 30 sec and refresh.")

if auto_refresh:
    time.sleep(5)
    st.rerun()
else:
    if st.button("Refresh Now"):
        st.rerun()

st.markdown("---")
st.caption("Powered by CoinGecko API | Auto refreshes every 5 sec")
