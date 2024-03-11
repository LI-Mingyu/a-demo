import streamlit as st
import logging
from datetime import datetime
import uuid

import anthropic

# Set the logging level
logging.basicConfig(level=logging.INFO)

LLM = "claude-3-opus-20240229"
# Generate a UUID for the session
session_id = str(uuid.uuid4())
# Get the current timestamp
timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
# Log the session ID and timestamp
logging.info(f"Session ID: {session_id}, Timestamp: {timestamp}")

# Helper functions
def process_messages(messages):
    processed_messages = []
    for i, message in enumerate(messages):
        if i == 0 or message["role"] != messages[i - 1]["role"]:
            processed_messages.append(message)
        else:
            processed_messages[-1]["content"] += "\n" + message["content"]
    return processed_messages

# The streamlit script starts here
logging.info(f"[{session_id}] Starting Streamlit script ...")

st.set_page_config(
    page_title="Q&A Web App",
    page_icon="❓",
)
st.subheader("Q&A Web App with Claude-3 opus")
st.write("Welcome! I'm an AI assistant with knowledge in IT systems and programming. How can I help you today?")

if "messages" not in st.session_state.keys():
    # Initialize the session_state.messages
    st.session_state.messages = [{"role": "system", "content": "You are a helpful AI assistant."}]
else: # Since streamlit script is executed every time a widget is changed, this "else" is not necessary, but improves readability
    # Display chat messages
    for message in st.session_state.messages:
        if message["role"] == "user" or message["role"] == "assistant":
            with st.chat_message(message["role"]):
                st.write(message["content"])

# User-provided prompt
if user_prompt := st.chat_input():
    logging.info(f"[{session_id}] User's prompt: {user_prompt}")
    with st.chat_message("user"):
        st.write(user_prompt)
        st.session_state.messages.append({"role": "user", "content": user_prompt})
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                client = anthropic.Anthropic()
                system_message = next((m for m in st.session_state.messages if m["role"] == "system"), None)
                user_assistant_messages = [m for m in st.session_state.messages if m["role"] != "system"]
                processed_messages = process_messages(user_assistant_messages)

                with client.messages.stream(
                    max_tokens=1024,
                    messages=processed_messages,
                    model=LLM,
                    system=system_message["content"] if system_message else None,
                ) as stream:
                    resp_display = st.empty()
                    collected_resp_content = ""
                    for text in stream.text_stream:
                        collected_resp_content += text
                        resp_display.write(collected_resp_content)
            except Exception as e:
                logging.error(f"[{session_id}] Error generating response from Claude: {e}")
                st.error('An error occurred while generating the response. Please try again later.')
                st.stop()
            logging.info(f"[{session_id}] AI's response: {collected_resp_content[:150]}".replace("\n", "") + "..." + f"{collected_resp_content[-50:]}".replace("\n", ""))

    # Add the generated msg to session state
    st.session_state.messages.append({"role": "assistant", "content": collected_resp_content})

st.write("*Note: The generated responses are for reference only.*")
logging.info(f"[{session_id}] Streamlit script ended.")
