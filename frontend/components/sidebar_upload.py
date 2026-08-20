"""Sidebar component for uploading and managing knowledge base documents (admin)."""

import os

import requests
import streamlit as st

BACKEND_URL = os.getenv("BACKEND_URL", "http://backend:8000")


def render_sidebar_upload() -> None:
    with st.sidebar:
        st.header("Manage Knowledge Base")

        uploaded_file = st.file_uploader(
            "Upload a document", type=["pdf", "docx", "txt", "md"]
        )
        if st.button("Upload", disabled=uploaded_file is None):
            _upload_document(uploaded_file)

        st.subheader("Indexed Documents")
        _render_document_list()


def _upload_document(uploaded_file) -> None:
    try:
        files = {"file": (uploaded_file.name, uploaded_file.getvalue())}
        response = requests.post(f"{BACKEND_URL}/ingest", files=files, timeout=120)
        response.raise_for_status()
        data = response.json()
        st.toast(
            f"Uploaded '{data['filename']}' — {data['chunks_added']} chunks added.",
            icon="✅",
        )
    except requests.RequestException as exc:
        st.toast(f"Upload failed: {exc}", icon="❌")
        return

    st.rerun()


def _render_document_list() -> None:
    try:
        response = requests.get(f"{BACKEND_URL}/documents", timeout=30)
        response.raise_for_status()
        sources = response.json()["sources"]
    except requests.RequestException as exc:
        st.error(f"Couldn't load indexed documents: {exc}")
        return

    if not sources:
        st.caption("No documents indexed yet.")
        return

    for filename in sources:
        col1, col2 = st.columns([4, 1])
        col1.write(filename)
        if col2.button("Remove", key=f"remove_{filename}"):
            _delete_document(filename)


def _delete_document(filename: str) -> None:
    try:
        response = requests.delete(f"{BACKEND_URL}/documents/{filename}", timeout=30)
        response.raise_for_status()
        st.toast(f"Removed '{filename}'.", icon="✅")
    except requests.RequestException as exc:
        st.toast(f"Failed to remove '{filename}': {exc}", icon="❌")

    st.rerun()
