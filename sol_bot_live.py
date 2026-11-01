import streamlit as st
import ccxt

st.set_page_config(page_title="REAL ETH Trader 10% - Bybit", layout="wide")
st.title("💎 REAL AUTO TRADER - ETH/USDT - 10% Fee - BYBIT")
st.markdown("### REAL Bybit ETH Trading + 10% Profit Share")

OWNER_WALLET = "0x2a61af0ae226bb231d593c749ca1dc07cba3a647"

with st.sidebar:
    st.subheader("🔑 YOUR Bybit (Real Money)")
    api_key = st.text_input("Bybit API Key", type="password")
    api_secret = st.text_input("Bybit Secret", type="password")
    trade_amount = st.number_input("Trade Amount USDT", value=20.0)
    st.divider()
    st.subheader("Settings - ETH")
    enable_trade = st.checkbox("ENABLE REAL AUTO TRADE")
    buy_below = st.number_input("Auto BUY ETH Below $", value=3000.0)
    sell_above = st.number_input("Auto SELL ETH Above $", value=3500.0)
    st.divider()
    st.success(f"💰 Owner Wallet (10% ETH):")
    st.code(OWNER_WALLET)

# LIVE ETH PRICE - Kraken works on Streamlit US servers
eth_price = None
for ex_id in ['kraken', 'coinbase', 'kucoin', 'bitstamp']:
    try:
        ex = getattr(ccxt, ex_id)()
        ticker = ex.fetch_ticker('ETH/USDT')
        eth_price = ticker['last']
        st.metric(f"ETH/USDT LIVE ({ex_id.upper()})", f"${eth_price:,.2f}")
        st.caption(f"Live price from {ex_id} - Trades execute on YOUR Bybit")
        break
    except:
        continue

if not eth_price:
    import requests
    try:
        r = requests.get("https://api.coingecko.com/api/v3/simple/price?ids=ethereum&vs_currencies=usd", timeout=5).json()
        eth_price = r['ethereum']['usd']
        st.metric("ETH/USDT LIVE (CoinGecko)", f"${eth_price:,.2f}")
    except Exception as e:
        st.error(f"Price Error: {e}")
        st.stop()

st.write(f"Strategy: Buy ETH < ${buy_below} | Sell ETH > ${sell_above}")

if eth_price < buy_below:
    st.success(f"🟢 BUY SIGNAL - ETH ${eth_price} < ${buy_below}")
    signal = "BUY"
elif eth_price > sell_above:
    st.error(f"🔴 SELL SIGNAL - ETH ${eth_price} > ${sell_above}")
    signal = "SELL"
else:
    st.warning(f"🟡 HOLD - ETH ${eth_price} between levels")
    signal = "HOLD"

st.subheader("Real Trading Panel - BYBIT - 10% Fee - ETH/USDT")
if st.button(f"{signal} ETH NOW (Real - Bybit)"):
    if not api_key or not api_secret:
        st.error("Enter your Bybit API Key & Secret first!")
    elif not enable_trade:
        st.error("Check ENABLE REAL AUTO TRADE in sidebar!")
    else:
        try:
            exchange = ccxt.bybit({
                'apiKey': api_key, 
                'secret': api_secret, 
                'enableRateLimit': True
            })
            balance = exchange.fetch_balance()
            usdt = balance['total'].get('USDT', 0)
            eth_bal = balance['total'].get('ETH', 0)
            st.write(f"Your Bybit Balances - USDT: {usdt} | ETH: {eth_bal}")
            st.success("Bybit Connection OK - Ready to trade REAL ETH!")
            
            if signal == "BUY":
                st.info(f"Would BUY {(trade_amount/eth_price):.4f} ETH for ${trade_amount} USDT on Bybit")
                st.warning("Click again to confirm real trade - Enable trading in Bybit API first")
            else:
                st.info(f"Would SELL {eth_bal} ETH on Bybit")
                
            st.info(f"💰 10% Fee: If profit = $100, user sends $10 USDT to owner")

        except Exception as e:
            st.error(f"Bybit Error: {e}")
            st.write("Fix: Bybit API → Edit Key → Permissions: Spot Trade + Read | IP: No restriction")

# REAL TRADE EXECUTION
if st.button(f"🔥 CONFIRM REAL {signal} ETH ON BYBIT"):
    if not api_key or not api_secret or not enable_trade:
        st.error("Enter keys + enable trading first!")
    else:
        try:
            exchange = ccxt.bybit({'apiKey': api_key, 'secret': api_secret, 'enableRateLimit': True})
            if signal == "BUY":
                amount_eth = trade_amount / eth_price
                order = exchange.create_market_buy_order('ETH/USDT', amount_eth)
                st.success(f"BOUGHT REAL ETH! Order ID: {order['id']} | Amount: {amount_eth} ETH")
                st.balloons()
            elif signal == "SELL":
                bal = exchange.fetch_balance()
                eth_to_sell = bal['free'].get('ETH', 0)
                if eth_to_sell > 0.001:
                    order = exchange.create_market_sell_order('ETH/USDT', eth_to_sell)
                    st.success(f"SOLD REAL ETH! Order ID: {order['id']}")
                else:
                    st.error("No ETH to sell - Buy first")
            st.write(f"💸 Remember: 10% profit goes to owner wallet below")
        except Exception as e:
            st.error(f"Trade Failed: {e}")

st.divider()
st.subheader("💰 How 10% Profit Share Works - ETH")
st.write("1. User enters THEIR Bybit API Key (you never hold money)")
st.write("2. Bot trades REAL ETH/USDT on THEIR Bybit account")
st.write("3. You collect 10% profit - Example: $100 profit = $10 USDT")
st.code(OWNER_WALLET, language="text")
st.warning(f"⬆️ Send 10% USDT (BEP20 CHEAP FEE) to: {OWNER_WALLET}")
st.info("💡 SAME address works on BEP20 (fee $0.20) and ERC20 (fee $10). Use BEP20!")
st.success("ETH Trading + 10% Fee = More users, cheaper gas on BEP20!")
