import os
import streamlit as st
import google.generativeai as genai

st.title("CryptoBot")
st.write("Welcome to CryptoBot! Ask me anything about cryptocurrency — from how Bitcoin works, to understanding blockchain, to the history of your favorite coins.")

key = os.environ["GEMINI_API_KEY"]  
genai.configure(api_key=key)

def chatbot_logic():
    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    chatPrompt = st.chat_input("Ask CryptoBot a question...")

    if chatPrompt:
        st.session_state.messages.append({"role": "user", "content": chatPrompt})
        with st.chat_message("user"):
            st.write(chatPrompt)

        model = genai.GenerativeModel("gemini-3-flash-preview")
    
        history = ""
        for message in st.session_state.messages:
            history += message["role"] + ": " + message["content"] + "\n"

        prompt = (
            "You are a cryptocurrency expert chatbot. Only answer questions related to "
            "cryptocurrency, blockchain, and related topics.\n\n"
            "Here is the conversation so far:\n" + history + "\n"
            "Now answer the user's latest question."
        )

        try:
            response = model.generate_content(prompt)
            with st.chat_message("assistant"):
                st.write(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
        except Exception as anyerror:
            st.write("Error: " + str(anyerror))

chatbot_logic()