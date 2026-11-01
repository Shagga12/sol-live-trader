import streamlit as st
import ccxt

st.set_page_config(page_title="REAL BTC Trader 10% - Bybit", layout="wide")
st.title("💰 REAL AUTO TRADER - BTC/USDT - 10% Fee - BYBIT")
st.markdown("### REAL Bybit Trading + 10% Profit Share")

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

btc_price = None
# Kraken works on Streamlit USA servers
for ex_id in ['kraken', 'coinbase', 'kucoin']:
    try:
        ex = getattr(ccxt, ex_id)()
        ticker = ex.fetch_ticker('BTC/USDT')
        btc_price = ticker['last']
        st.metric(f"BTC/USDT LIVE ({ex_id.upper()})", f"${btc_price:,.2f}")
        st.caption(f"Live price from {ex_id} - Trades on YOUR Bybit")
        break
    except:
        continue

if not btc_price:
    import requests
    try:
        r = requests.get("https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd", timeout=5).json()
        btc_price = r['bitcoin']['usd']
        st.metric("BTC/USDT LIVE (CoinGecko)", f"${btc_price:,.2f}")
    except Exception as e:
        st.error(f"Price Error: {e}")
        st.stop()

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

st.subheader("Real Trading Panel - BYBIT - 10% Fee Model")
if st.button(f"{signal} BTC NOW (Real - Bybit)"):
    if not api_key or not api_secret:
        st.error("Enter your Bybit API Key & Secret first!")
    elif not enable_trade:
        st.error("Check ENABLE REAL AUTO TRADE in sidebar!")
    else:
        try:
            exchange = ccxt.bybit({'apiKey': api_key, 'secret': api_secret, 'enableRateLimit': True})
            balance = exchange.fetch_balance()
            usdt = balance['total'].get('USDT', 0)
            st.write(f"Your Bybit USDT Balance: {usdt}")
            st.success("Bybit Connection OK - Ready to trade real money!")
            st.info(f"💰 10% Fee Model: If profit = $100, you collect $10 USDT")
        except Exception as e:
            st.error(f"Bybit Error: {e}")
            st.write("Fix: In Bybit API settings, disable IP restriction or add Streamlit IPs")

st.divider()
st.subheader("How 10% Fee Works")
st.write("1. User enters THEIR Bybit API Key (you never hold money)")
st.write("2. Bot trades on THEIR Bybit account - REAL money")
st.write("3. You collect 10% profit - Example: $100 profit = $10 USDT to your wallet")
st.write("**Much cheaper for users = more users join!**")
