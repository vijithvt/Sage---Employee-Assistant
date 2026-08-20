"""Component for displaying source citations under assistant chat messages."""

import streamlit as st


def render_sources(sources: list[dict]) -> None:
    if not sources:
        return

    filenames = sorted({source["filename"] for source in sources})
    with st.expander(f"Sources ({len(filenames)})"):
        for filename in filenames:
            st.markdown(f"- {filename}")
