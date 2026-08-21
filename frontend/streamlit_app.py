"""Streamlit frontend entrypoint for the Sage — Employee AI Assistant chat UI."""

import streamlit as st

from components.chat_ui import render_chat
from components.sidebar_upload import render_sidebar_upload

st.set_page_config(page_title="Sage", page_icon="🌿")
st.title("Sage")
st.caption("Your Employee AI Assistant")

render_sidebar_upload()
render_chat()
