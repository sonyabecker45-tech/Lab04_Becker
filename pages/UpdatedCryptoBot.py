import streamlit as st
import requests
import google.generativeai as genai
import os
import json

st.set_page_config(page_title="CryptoBot", page_icon="🤖", layout="wide")
st.title("CryptoBot with API Data")
st.write(
    "This chatbot uses live cryptocurrency data from the CoinGecko API and the Google Gemini LLM. "
    "It also remembers the ongoing conversation."
)

api_key = os.environ["GEMINI_API_KEY"]
genai.configure(api_key=api_key)
default_coin = st.text_input("What cryptocurrency do you want to explore?", value="Bitcoin")

def chatHistoryString(chat_history):
    history = ""
    for message in chat_history:
        if message["role"] == "user":
            history += "User: " + message["content"] + "\n"
        else:
            history += "CryptoBot: " + message["content"] + "\n"
    return history

if "updated_crypto_messages" not in st.session_state:
    st.session_state.updated_crypto_messages = [
        {
            "role": "assistant",
            "content": "Hello! I'm CryptoBot, your cryptocurrency guide. Ask me about coins, blockchain, market trends, or crypto basics!"
        }
    ]

for message in st.session_state.updated_crypto_messages:
    if message["role"] == "user":
        with st.chat_message("user"):
            st.markdown(message["content"])
    else:
        with st.chat_message("assistant"):
            st.markdown(message["content"])





chatPrompt = st.chat_input("Enter message here")
def getCryptoJson(coinName: str):
    try:
        coin_id = coinName.lower().replace(" ", "-")

        crypto_resp = requests.get(
            "https://api.coingecko.com/api/v3/coins/" + coin_id,
            params={
                "localization": "false",
                "tickers": "false",
                "market_data": "true"
            },
            timeout=10,
        )

        crypto_resp.raise_for_status()
        crypto_data = crypto_resp.json()

        if not crypto_data.get("market_data"):
            return None

        market = crypto_data["market_data"]

        return {
            "name": crypto_data["name"],
            "symbol": crypto_data["symbol"],
            "price": market["current_price"]["usd"],
            "market_cap": market["market_cap"]["usd"],
            "volume": market["total_volume"]["usd"],
            "change_24h": market["price_change_percentage_24h"]
        }

    except:
        return None


def askGemini(api_key, chat_history, user_message, crypto_json):
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-3-flash-preview")
        history_str = chatHistoryString(chat_history)
        if crypto_json is not None:
            crypto_str = json.dumps(crypto_json, indent=2)
        else:
            crypto_str = "No cryptocurrency API data is currently available."

        prompt = f"""
You are CryptoBot, a helpful cryptocurrency chatbot inside a Streamlit app.
Here is the conversation so far:
{history_str}
Here is live cryptocurrency data from the CoinGecko API:
{crypto_str}
Here is the user's new question:
{user_message}
Keep your answer short, clear, and helpful.
"""
        response = model.generate_content(prompt)
        if not response.text:
            return "CryptoBot could not make a response this time."
        return response.text
    except Exception as e:
        return "CryptoBot error: " + str(e)

if chatPrompt:
    crypto_info = getCryptoJson(default_coin)
    user_message = {"role": "user", "content": chatPrompt}
    st.session_state.updated_crypto_messages.append(user_message)
    with st.chat_message("user"):
        st.markdown(chatPrompt)

    with st.chat_message("assistant"):
        with st.spinner("CryptoBot is thinking..."):
            ans = askGemini(
                api_key=api_key,
                chat_history=st.session_state.updated_crypto_messages,
                user_message=chatPrompt,
                crypto_json=crypto_info,
            )
            st.markdown(ans)

    bot_message = {"role": "assistant", "content": ans}
    st.session_state.updated_crypto_messages.append(bot_message)
            
        




