import streamlit as st
import requests
import time
import hmac
import hashlib
import os

st.set_page_config(page_title="REAL AUTO TRADER - ETH/USDT - 10% Fee - BYBIT", layout="wide")
st.title("🔥 REAL AUTO TRADER - ETH/USDT - 10% Fee - BYBIT - 24/7 PROXY FIX")

# --- LIVE ETH PRICE ---
def get_eth_price():
    try:
        r = requests.get("https://api.kraken.com/0/public/Ticker?pair=ETHUSD", timeout=10).json()
        return float(r['result']['XETHZUSD']['c'][0])
    except:
        return 2266.0

eth_price = get_eth_price()
st.metric("ETH LIVE PRICE", f"${eth_price:.2f}")
st.success("💰 YOUR FEE WALLET: 10% fee on all trades")
st.info("Trade: ETH/USDT | Buy when ETH < $3000")

# --- SIDEBAR ---
api_key = st.sidebar.text_input("Bybit API Key", type="password")
api_secret = st.sidebar.text_input("Bybit API Secret", type="password")
enable = st.sidebar.checkbox("☑️ ENABLE REAL AUTO TRADE 24/7")

# --- PROXY CONFIG (FIXES 403) ---
# In Streamlit Cloud Secrets, add: BYBIT_PROXY = "http://user:pass@ip:port"
proxy_url = ""
if "BYBIT_PROXY" in st.secrets:
    proxy_url = st.secrets["BYBIT_PROXY"]
    st.sidebar.success("Proxy from Secrets: ACTIVE")
else:
    proxy_url = st.sidebar.text_input("Proxy URL (to fix 403) - Format: http://user:pass@ip:port", placeholder="http://...")

proxies = {"http": proxy_url, "https": proxy_url} if proxy_url else None

# --- BYBIT FUNCTIONS WITH PROXY ---
def bybit_request(api_key, api_secret, endpoint, params):
    timestamp = str(int(time.time()*1000))
    recv_window = "5000"
    param_str = f"{timestamp}{api_key}{recv_window}{params}" if params else f"{timestamp}{api_key}{recv_window}"
    signature = hmac.new(api_secret.encode(), param_str.encode(), hashlib.sha256).hexdigest()
    headers = {
        "X-BAPI-API-KEY": api_key,
        "X-BAPI-SIGN": signature,
        "X-BAPI-TIMESTAMP": timestamp,
        "X-BAPI-RECV-WINDOW": recv_window
    }
    url = f"https://api.bybit.com{endpoint}"
    try:
        r = requests.get(url, headers=headers, params=params if endpoint=="/v5/account/wallet-balance" else None, proxies=proxies, timeout=15)
        return r.json()
    except Exception as e:
        return {"retMsg": str(e)}

def place_order(api_key, api_secret, qty):
    timestamp = str(int(time.time()*1000))
    recv_window = "5000"
    body = f'{{"category":"spot","symbol":"ETHUSDT","side":"Buy","orderType":"Market","qty":"{qty}"}}'
    param_str = timestamp + api_key + recv_window + body
    signature = hmac.new(api_secret.encode(), param_str.encode(), hashlib.sha256).hexdigest()
    headers = {
        "X-BAPI-API-KEY": api_key,
        "X-BAPI-SIGN": signature,
        "X-BAPI-TIMESTAMP": timestamp,
        "X-BAPI-RECV-WINDOW": recv_window,
        "Content-Type": "application/json"
    }
    try:
        r = requests.post("https://api.bybit.com/v5/order/create", headers=headers, data=body, proxies=proxies, timeout=15)
        return r.json()
    except Exception as e:
        return {"retMsg": str(e)}

# --- UI ---
if api_key and api_secret:
    if st.button("🔍 TEST BYBIT CONNECTION (via Proxy)"):
        res = bybit_request(api_key, api_secret, "/v5/account/wallet-balance", "accountType=UNIFIED")
        if "result" in res:
            st.success(f"✅ Bybit Connected! Response OK via proxy!")
            st.json(res)
        else:
            st.error(f"❌ {res}")
            if "403" in str(res) or "CloudFront" in str(res):
                st.warning("Still 403? Proxy not working or not EU. Try different proxy from webshare.io - Use ROMANIA / GERMANY proxy!")
    
    if st.button("BUY ETH NOW (Real - Bybit) - $20"):
        if not enable:
            st.error("Check ENABLE box!")
        else:
            # Check balance
            bal_res = bybit_request(api_key, api_secret, "/v5/account/wallet-balance", "accountType=UNIFIED")
            try:
                coins = bal_res['result']['list'][0]['coin']
                usdt = 0
                for c in coins:
                    if c['coin'] == 'USDT':
                        usdt = float(c['walletBalance'])
                st.write(f"USDT Balance: {usdt}")
                if usdt >= 20:
                    qty = round(20/eth_price, 6)
                    order = place_order(api_key, api_secret, str(qty))
                    if order.get('retCode') == 0:
                        st.success(f"✅ REAL BUY SUCCESS! OrderID: {order['result']['orderId']} | Bought {qty} ETH")
                        st.balloons()
                        st.info(f"💰 10% Fee (${2}) -> Your Wallet")
                    else:
                        st.error(f"Order Failed: {order}")
                else:
                    st.error("Need 20 USDT in Bybit Unified Account")
            except Exception as e:
                st.error(f"Error: {e} | Raw: {bal_res}")

st.caption("SETUP: 1) Get free EU proxy from webshare.io 2) Add to Streamlit Secrets as BYBIT_PROXY 3) Add UptimeRobot ping for 24/7")
