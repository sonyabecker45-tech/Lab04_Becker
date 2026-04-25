import streamlit as st
import requests
import plotly.express as px
import time

st.title("CoinScope")
st.write("Explore live cryptocurrency data!")
API_KEY = st.secrets["key"]

def show_top10():
    with st.expander("Top 10 Coins by Market Cap"):
        url3 = "https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&order=market_cap_desc&per_page=10&page=1"
        r3 = requests.get(url3, headers={"x_cg_demo_api_key": API_KEY})
        data3 = r3.json()

        if not isinstance(data3, list):
            st.write("Data unavailable, please try again.")
            return

        names = []
        market_caps = []

        for coin in data3:
            names.append(coin["name"])
            market_caps.append(coin["market_cap"])

        fig2 = px.bar(
            x=names,
            y=market_caps,
            title="Top 10 Coins by Market Cap",
            labels={"x": "Coin", "y": "Market Cap (USD)"}
        )

        st.plotly_chart(fig2)

def show_coin_info():
    coin_id = st.selectbox("Select a coin:", ["bitcoin", "ethereum", "dogecoin", "cardano", "solana"])
    days = st.slider("How many days of price history", 7, 90, 30)

    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}"
    r = requests.get(url, headers={"x_cg_demo_api_key": API_KEY})
    data = r.json()

    try:
        st.image(data["image"]["large"])
    except:
        st.warning("Image unavailable.")

    try:
        st.write("**Coin:** " + data["name"])
        st.write("**Current Price:** $" + str(data["market_data"]["current_price"]["usd"]))
        st.write("**Market Cap:** $" + str(data["market_data"]["market_cap"]["usd"]))
        st.write("**24h Change:** " + str(round(data["market_data"]["price_change_percentage_24h"], 2)) + "%")
        st.markdown("---")
    except:
        st.warning("Coin data is temporarily unavailable.")
        return coin_id, days, {}

    return coin_id, days, data


def show_price_history(coin_id, days, data):
    time.sleep(1)

    url2 = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart?vs_currency=usd&days={days}"
    r2 = requests.get(url2, headers={"x_cg_demo_api_key": API_KEY})
    data2 = r2.json()

    if "prices" not in data2:
        st.write("Price history unavailable, please try again.")
    else:
        dates = []
        prices = []

        for point in data2["prices"]:
            dates.append(point[0])
            prices.append(point[1])

        total = 0
        for price in prices:
            total += price

        average_price = total / len(prices)

        st.write("**Average Price over " + str(days) + " days:** $" + str(round(average_price, 2)))

        fig = px.line(
            x=dates,
            y=prices,
            title=data["name"] + " Price - Last " + str(days) + " Days",
            labels={"x": "Date", "y": "Price (USD)"}
        )

        st.plotly_chart(fig)

show_top10()

coin_id, days, data = show_coin_info()

if data:
    show_price_history(coin_id, days, data)