"""Unit tests for backend/app/core/chunking.py."""

from app.core.chunking import chunk_text


def test_chunk_text_normal():
    text = "a" * 2000
    chunks = chunk_text(text, chunk_size=800, chunk_overlap=120, metadata={"source": "doc.txt"})

    assert len(chunks) > 1
    for i, chunk in enumerate(chunks):
        assert chunk["metadata"]["source"] == "doc.txt"
        assert chunk["metadata"]["chunk_index"] == i
        assert len(chunk["text"]) <= 800

    # Verify overlap: end of one chunk should share content with the start of the next.
    first_end = chunks[0]["text"][-50:]
    second_start = chunks[1]["text"][:120]
    assert any(c in second_start for c in [first_end[-10:]])


def test_chunk_text_shorter_than_chunk_size():
    text = "short document text"
    chunks = chunk_text(text, chunk_size=800, chunk_overlap=120, metadata={"source": "doc.txt"})

    assert len(chunks) == 1
    assert chunks[0]["text"] == text
    assert chunks[0]["metadata"] == {"source": "doc.txt", "chunk_index": 0}


def test_chunk_text_empty():
    chunks = chunk_text("", chunk_size=800, chunk_overlap=120, metadata={"source": "doc.txt"})
    assert chunks == []

    chunks_whitespace = chunk_text("   \n  ", chunk_size=800, chunk_overlap=120, metadata={"source": "doc.txt"})
    assert chunks_whitespace == []
