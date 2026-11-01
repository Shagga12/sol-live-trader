import streamlit as st
import ccxt
import time

st.set_page_config(page_title="REAL BTC Trader 20% - Bybit", layout="wide")
st.title("💰 REAL AUTO TRADER - BTC/USDT - 20% Fee - BYBIT")

st.markdown("### REAL Bybit Trading + Profit Share")

with st.sidebar:
    st.subheader("🔑 YOUR Bybit (Real Money)")
    api_key = st.text_input("Bybit API Key", type="password")
    api_secret = st.text_input("Bybit Secret", type="password")
    trade_amount = st.number_input("Trade Amount USDT", value=20.0)
    st.divider()
    st.subheader("Settings")
    enable_trade = st.checkbox("ENABLE REAL AUTO TRADE")
    buy_below = st.number_input("Auto BUY BTC Below $", value=67000.0)
    sell_above = st.number_input("Auto SELL BTC Above $", value=70000.0)

# LIVE PRICE - FROM BINANCE (works everywhere) but TRADES on Bybit
try:
    exchange_public = ccxt.binance()
    ticker = exchange_public.fetch_ticker('BTC/USDT')
    btc_price = ticker['last']
    st.metric("BTC/USDT LIVE", f"${btc_price:,.2f}")
    st.caption("Price from Binance (public) - Trades execute on YOUR Bybit")
    st.write(f"Strategy: Buy < {buy_below} | Sell > {sell_above}")

    if btc_price < buy_below:
        st.success(f"🟢 BUY SIGNAL - BTC {btc_price} < {buy_below}")
        signal = "BUY"
    elif btc_price > sell_above:
        st.error(f"🔴 SELL SIGNAL - BTC {btc_price} > {sell_above}")
        signal = "SELL"
    else:
        st.warning(f"🟡 HOLD - BTC {btc_price} between levels")
        signal = "HOLD"

    st.subheader("Real Trading Panel - BYBIT")
    if st.button(f"{signal} BTC NOW (Real - Bybit)"):
        if not api_key or not api_secret:
            st.error("Enter your Bybit API Key & Secret first!")
        elif not enable_trade:
            st.error("Check ENABLE REAL AUTO TRADE in sidebar!")
        else:
            try:
                exchange = ccxt.bybit({
                    'apiKey': api_key,
                    'secret': api_secret,
                    'enableRateLimit': True,
                })
                balance = exchange.fetch_balance()
                usdt = balance['USDT']['free']
                st.write(f"Your Bybit USDT Balance: {usdt}")

                if signal == "BUY" and usdt >= trade_amount:
                    order = exchange.create_market_buy_order('BTC/USDT', trade_amount / btc_price)
                    st.success(f"BOUGHT REAL BTC on Bybit! Order: {order['id']}")
                elif signal == "SELL":
                    btc_bal = balance['BTC']['free']
                    if btc_bal > 0:
                        order = exchange.create_market_sell_order('BTC/USDT', btc_bal)
                        st.success(f"SOLD REAL BTC on Bybit! Order: {order['id']}")
                    else:
                        st.error("No BTC to sell on Bybit")
                else:
                    st.warning("Not enough USDT or no signal")

            except Exception as e:
                st.error(f"Bybit Trade Error (check your keys): {e}")

except Exception as e:
    st.error(f"Price Error: {e}")
    st.info("Trying backup price source...")
    try:
        exchange_public = ccxt.kraken()
        ticker = exchange_public.fetch_ticker('BTC/USDT')
        st.metric("BTC/USDT LIVE (Kraken backup)", f"${ticker['last']:,.2f}")
    except:
        pass

st.divider()
st.subheader("For Your Users - 20% Model")
st.write("1. User enters THEIR Bybit API Key (you never hold money)")
st.write("2. Bot trades on THEIR Bybit account")
st.write("3. You collect 20% profit in USDT to your wallet")
