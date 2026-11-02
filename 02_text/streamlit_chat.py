"""General chat demo. Start with streamlit run 02_text/streamlit_chat.py."""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import streamlit as st
from ai_lab import AzureSettings, chat


st.set_page_config(page_title="Azure Chat Lab", page_icon="💬")
st.title("Azure Chat Lab")
st.caption("A general chat demonstration using your Azure OpenAI deployment.")
try:
    AzureSettings.load("text")
except ValueError as error:
    st.info(str(error))
    st.stop()

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": "You are a concise, helpful information assistant."}]
if st.sidebar.button("Clear conversation"):
    st.session_state.messages = st.session_state.messages[:1]
    st.rerun()
for message in st.session_state.messages[1:]:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if text := st.chat_input("Enter a message"):
    with st.chat_message("user"):
        st.markdown(text)
    candidate = st.session_state.messages + [{"role": "user", "content": text}]
    try:
        with st.spinner("Generating a reply..."):
            answer = chat(candidate)
    except Exception:
        st.error("Request failed. Check credentials, deployment access, quota, and connectivity.")
    else:
        st.session_state.messages = candidate + [{"role": "assistant", "content": answer}]
        with st.chat_message("assistant"):
            st.markdown(answer)
