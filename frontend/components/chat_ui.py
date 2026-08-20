"""Chat interface component: renders chat history and handles Q&A with the backend."""

import os

import requests
import streamlit as st

from components.source_display import render_sources

BACKEND_URL = os.getenv("BACKEND_URL", "http://backend:8000")


def render_chat() -> None:
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "feedback_submitted" not in st.session_state:
        st.session_state.feedback_submitted = set()

    for index, message in enumerate(st.session_state.messages):
        _render_message(index, message)

    question = st.chat_input("Ask a question about company policies...")
    if not question:
        return

    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        with st.spinner("Thinking... (answers run on a local LLM and can take a while on CPU)"):
            try:
                response = requests.post(
                    # Local CPU inference is much slower than a cloud API, and the
                    # first query on a fresh install also pays a one-time model
                    # pull cost — so this timeout is generous on purpose.
                    f"{BACKEND_URL}/query", json={"question": question}, timeout=300
                )
                response.raise_for_status()
                data = response.json()
                answer = data["answer"]
                sources = data.get("sources", [])
            except requests.RequestException as exc:
                answer = f"⚠️ Sorry, I couldn't reach the knowledge base backend. ({exc})"
                sources = []
        st.markdown(answer)
        render_sources(sources)

        assistant_message = {
            "role": "assistant",
            "content": answer,
            "sources": sources,
            "question": question,
        }
        st.session_state.messages.append(assistant_message)
        _render_feedback(len(st.session_state.messages) - 1, assistant_message)


def _render_message(index: int, message: dict) -> None:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if message["role"] == "assistant":
            render_sources(message.get("sources", []))
            _render_feedback(index, message)


def _render_feedback(index: int, message: dict) -> None:
    rating_value = st.feedback("thumbs", key=f"feedback_{index}")

    if rating_value is None or index in st.session_state.feedback_submitted:
        return

    rating = "up" if rating_value == 1 else "down"
    try:
        requests.post(
            f"{BACKEND_URL}/feedback",
            json={
                "question": message.get("question", ""),
                "answer": message["content"],
                "rating": rating,
                "sources": message.get("sources", []),
            },
            timeout=10,
        )
        st.session_state.feedback_submitted.add(index)
        st.caption("Thanks for the feedback!")
    except requests.RequestException:
        st.caption("Couldn't submit feedback right now.")
