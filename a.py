import streamlit as st
import logging
import os
import anthropic
from anthropic import Anthropic
from streamlit import runtime

# Helper function
def process_messages(messages):
    processed_messages = []
    for i, message in enumerate(messages):
        if i == 0 or message["role"] != messages[i - 1]["role"]:
            processed_messages.append(message)
        else:
            processed_messages[-1]["content"] += "\n" + message["content"]
    return processed_messages

# Streamlit app
st.set_page_config(
    page_title="Q&A Web App",
    page_icon="❓",
)

st.header("Q&A Web App")
st.write("Welcome! I'm an AI assistant. How can I help you today?")

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": "You are a helpful AI assistant."}]

for message in st.session_state.messages:
    if message["role"] == "user" or message["role"] == "assistant":
        with st.chat_message(message["role"]):
            st.write(message["content"])

user_prompt = st.chat_input("Enter your question:")

if user_prompt:
    with st.chat_message("user"):
        st.write(user_prompt)
    st.session_state.messages.append({"role": "user", "content": user_prompt})
    with st.chat_message("assistant"):
        with st.spinner("Generating response..."):
            try:
                client = anthropic.Anthropic()
                system_message = next((m for m in st.session_state.messages if m["role"] == "system"), None)
                user_assistant_messages = [m for m in st.session_state.messages if m["role"] != "system"]
                processed_messages = process_messages(user_assistant_messages)

                with client.messages.stream(
                    max_tokens=1024,
                    messages=processed_messages,
                    model="claude-3-opus-20240229",
                    system=system_message["content"] if system_message else None,
                ) as stream:
                    resp_display = st.empty()
                    collected_resp_content = ""
                    for text in stream.text_stream:
                        collected_resp_content += text
                        resp_display.write(collected_resp_content)
            except Exception as e:
                logging.error(f"Error generating response: {e}")
                st.error('An error occurred while generating the response. Please try again later.')

    st.session_state.messages.append({"role": "assistant", "content": collected_resp_content})

st.write("*Note: The generated responses are for reference only.*")
logging.info("Streamlit script ended.")
