import streamlit as st
import requests
import google.generativeai as genai

COINGECKO_KEY = st.secrets["key"]
GEMINI_KEY = st.secrets["GEMINI_API_KEY"]

genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel("gemini-2.5-flash")

st.title("Processing Web API Data 📈")
st.write("Learn about cryptocurrency using live CoinGecko API data and Gemini AI explanations.")
st.write("---")

with st.container(border=True):
    st.subheader("Step 1: Choose Your Crypto Settings")

    col1, col2 = st.columns(2)

    with col1:
        coin_id = st.selectbox(
            "Choose a cryptocurrency:",
            ["bitcoin", "ethereum", "dogecoin", "cardano", "solana"]
        )

    with col2:
        days = st.slider("Days of price history:", 7, 90, 30)

    with st.expander("Step 2: Customize AI Output Style", expanded=True):
        style = st.radio(
            "Choose the type of explanation:",
            [
                "Beginner Explanation",
                "Investor Report",
                "News Article",
                "Risk Analysis"
            ]
        )

        if style == "Beginner Explanation":
            st.info("Explains the crypto data in simple terms for beginners.")
        elif style == "Investor Report":
            st.info("Gives a simple investment-style summary.")
        elif style == "News Article":
            st.info("Written like a short crypto news report.")
        elif style == "Risk Analysis":
            st.warning("Focuses on risks and volatility.")

st.write("---")

with st.container(border=True):
    st.subheader("Step 3: Generate AI Crypto Analysis")

    if st.button("Generate Crypto Analysis"):
        try:
            with st.spinner("Generating AI crypto analysis...🤖"):
             
                coin_url = f"https://api.coingecko.com/api/v3/coins/{coin_id}"

                coin_response = requests.get(
                    coin_url,
                    headers={"x_cg_demo_api_key": COINGECKO_KEY}
                )
                coin_response.raise_for_status()
                coin_data = coin_response.json()

                coin_name = coin_data["name"]
                coin_symbol = coin_data["symbol"].upper()
                current_price = coin_data["market_data"]["current_price"]["usd"]
                market_cap = coin_data["market_data"]["market_cap"]["usd"]
                change_24h = coin_data["market_data"]["price_change_percentage_24h"]

          
                history_url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart?vs_currency=usd&days={days}"

                history_response = requests.get(
                    history_url,
                    headers={"x_cg_demo_api_key": COINGECKO_KEY}
                )
                history_response.raise_for_status()
                history_data = history_response.json()

                prices = [point[1] for point in history_data["prices"]]

                average_price = sum(prices) / len(prices)
                highest_price = max(prices)
                lowest_price = min(prices)

            
                Gprompt = f"""
You are explaining cryptocurrency to someone from the general population who is new and curious.

Use the following real data:

Coin: {coin_name}
Symbol: {coin_symbol}
Current Price: ${round(current_price, 2)}
Market Cap: ${market_cap}
24 Hour Change: {round(change_24h, 2)}%
Average Price (last {days} days): ${round(average_price, 2)}
Highest Price (last {days} days): ${round(highest_price, 2)}
Lowest Price (last {days} days): ${round(lowest_price, 2)}

Write a {style}.

Instructions:
- Use simple, clear language
- Explain what each number means
- Format the answer using short sections
- Use simple headings (like "Quick Summary" or "What This Means")
- Use bullet points when helpful
- Keep paragraphs short
- Make it easy to skim
- Do NOT use bold markdown symbols like **
- Do NOT give financial advice
"""

                response = model.generate_content(Gprompt)
                clean_text = response.text.replace("**", "")


            with st.container(border=True):
                st.subheader("Live Crypto Snapshot")

                st.write(
                    f"You are viewing live data for **{coin_name} ({coin_symbol})** "
                    f"over the last **{days} days**."
                )

                col1, col2, col3 = st.columns(3)

                with col1:
                    st.metric("Current Price", f"${round(current_price, 2)}")

                with col2:
                    st.metric("24h Change", f"{round(change_24h, 2)}%")

                with col3:
                    st.metric("Average Price", f"${round(average_price, 2)}")

                col4, col5 = st.columns(2)

                with col4:
                    st.metric("Highest Price", f"${round(highest_price, 2)}")

                with col5:
                    st.metric("Lowest Price", f"${round(lowest_price, 2)}")

       
            with st.container(border=True):
                st.subheader("Gemini Explanation")
                st.markdown(clean_text)

        
            with st.expander("How this page works"):
                st.write(
                    "This app uses the CoinGecko API to get live cryptocurrency data. "
                    "It calculates useful values like average, highest, and lowest prices. "
                    "Then it sends this data to Google Gemini, which explains it in simple terms."
                )

        except Exception as error:
            st.error("Something went wrong.")
            st.write(error)