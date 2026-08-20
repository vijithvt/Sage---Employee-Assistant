"""Unit tests for backend/app/core/vectorstore.py retrieval behavior."""

import importlib

import pytest


@pytest.fixture
def vectorstore_module(tmp_path, monkeypatch):
    """Reload vectorstore (and its config singleton) against a temp Chroma dir."""
    monkeypatch.setenv("CHROMA_PERSIST_DIR", str(tmp_path))

    from app.core import config, vectorstore

    importlib.reload(config)
    importlib.reload(vectorstore)

    yield vectorstore

    importlib.reload(config)


def _chunk(source: str, chunk_index: int, text: str) -> dict:
    return {"text": text, "metadata": {"source": source, "chunk_index": chunk_index}}


def test_add_then_retrieve_relevant_chunks(vectorstore_module):
    vectorstore_module.add_chunks(
        [
            _chunk("leave_policy.md", 0, "Employees receive 20 days of annual leave per year."),
            _chunk("leave_policy.md", 1, "Leave requests must be submitted two weeks in advance."),
            _chunk("it_helpdesk_sop.md", 0, "The IT helpdesk is open from 9am to 5pm on weekdays."),
        ]
    )

    results = vectorstore_module.similarity_search("How many leave days do employees get?", k=2)

    assert len(results) == 2
    for result in results:
        assert set(result) == {"text", "metadata", "score"}
    top_sources = {result["metadata"]["source"] for result in results}
    assert "leave_policy.md" in top_sources


def test_similarity_search_on_empty_collection_returns_empty(vectorstore_module):
    results = vectorstore_module.similarity_search("anything", k=5)
    assert results == []


def test_delete_source_removes_only_targeted_source(vectorstore_module):
    vectorstore_module.add_chunks(
        [
            _chunk("leave_policy.md", 0, "Employees receive 20 days of annual leave per year."),
            _chunk("it_helpdesk_sop.md", 0, "The IT helpdesk is open from 9am to 5pm on weekdays."),
        ]
    )

    vectorstore_module.delete_source("leave_policy.md")

    assert vectorstore_module.list_sources() == ["it_helpdesk_sop.md"]

    remaining = vectorstore_module.similarity_search("leave", k=10)
    assert all(r["metadata"]["source"] != "leave_policy.md" for r in remaining)
