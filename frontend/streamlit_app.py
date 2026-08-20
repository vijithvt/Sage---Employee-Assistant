"""Streamlit frontend entrypoint for the employee-kb-rag chat UI."""

import streamlit as st

from components.chat_ui import render_chat
from components.sidebar_upload import render_sidebar_upload

st.set_page_config(page_title="Sage", page_icon="🌿")
st.title("Sage")
st.caption("Ask Sage anything about company policy")

render_sidebar_upload()
render_chat()
