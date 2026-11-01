import streamlit as st
import requests
import time
import pandas as pd
from datetime import datetime
import ccxt

st.set_page_config(page_title="REAL BTC Trader 20%", page_icon="💰", layout="wide")

st.title("💰 REAL AUTO TRADER - BTC/USDT - 20% Fee")
st.markdown("**REAL Binance Trading + Profit Share**")

st.sidebar.header("🔑 YOUR Binance (Real Money)")
api_key = st.sidebar.text_input("Binance API Key", type="password")
api_secret = st.sidebar.text_input("Binance Secret", type="password")
investment_usdt = st.sidebar.number_input("Trade Amount USDT", value=20.0, min_value=5.0)
st.sidebar.divider()
st.sidebar.header("Settings")
auto_trade = st.sidebar.checkbox("ENABLE REAL AUTO TRADE", value=False)
buy_below = st.sidebar.number_input("Auto BUY BTC Below $", value=67000.0)
sell_above = st.sidebar.number_input("Auto SELL BTC Above $", value=70000.0)

st.sidebar.warning("⚠️ Use Binance API with 'Spot Trading' ONLY. No Withdrawal permission!")

def get_price():
    try:
        r = requests.get("https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd", timeout=10)
        return r.json()['bitcoin']['usd']
    except:
        return None

def trade_btc(action, amount_usdt):
    if not api_key or not api_secret:
        return "Add API keys first"
    try:
        exchange = ccxt.binance({
            'apiKey': api_key,
            'secret': api_secret,
            'enableRateLimit': True,
        })
        # Get balance
        balance = exchange.fetch_balance()
        usdt_balance = balance['USDT']['free']
        
        if action == "BUY":
            if usdt_balance < amount_usdt:
                return f"Not enough USDT. You have ${usdt_balance:.2f}"
            # Market buy BTC worth amount_usdt
            order = exchange.create_market_buy_order('BTC/USDT', amount_usdt)
            return f"BOUGHT! Order ID: {order['id']}"
        elif action == "SELL":
            btc_balance = balance['BTC']['free']
            if btc_balance < 0.0001:
                return f"Not enough BTC. You have {btc_balance}"
            order = exchange.create_market_sell_order('BTC/USDT', btc_balance)
            return f"SOLD! Order ID: {order['id']}"
    except Exception as e:
        return f"Trade Error: {str(e)}"

btc_price = get_price()

col1, col2 = st.columns(2)
with col1:
    st.metric("BTC/USDT LIVE", f"${btc_price:,.2f}" if btc_price else "Loading...")
    st.write(f"Strategy: Buy < ${buy_below} | Sell > ${sell_above}")

with col2:
    st.subheader("Real Trading Panel")
    if btc_price:
        if btc_price <= buy_below:
            st.success(f"🟢 BUY SIGNAL - BTC ${btc_price} < ${buy_below}")
            if auto_trade:
                result = trade_btc("BUY", investment_usdt)
                st.write(result)
                st.code(f"20% Fee owed on profit: Track in sheet")
            else:
                if st.button("BUY BTC NOW (Real)"):
                    st.write(trade_btc("BUY", investment_usdt))
        
        elif btc_price >= sell_above:
            st.error(f"🔴 SELL SIGNAL - BTC ${btc_price} > ${sell_above}")
            if auto_trade:
                result = trade_btc("SELL", investment_usdt)
                st.write(result)
            else:
                if st.button("SELL BTC NOW (Real)"):
                    st.write(trade_btc("SELL", investment_usdt))
        else:
            st.info(f"HOLD - Waiting for signal. Current ${btc_price}")

st.divider()
st.subheader("For Your Users - 20% Model")
st.write("1. User enters THEIR Binance API Key (you never hold money)")
st.write("2. Bot trades on THEIR account")
st.write("3. You track profit - they send you 20% to your USDT wallet")
st.code("Your Fee Wallet (TRC20): PASTE_YOUR_USDT_ADDRESS_HERE")
st.write("Future: Auto invoice via Telegram")

st.caption("LIVE REAL TRADING - Test with $20 first! This uses real money. BVI: No guarantee of profit.")

if auto_trade and btc_price:
    time.sleep(30)
    st.rerun()
