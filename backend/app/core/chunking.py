"""Text chunking utilities for splitting documents into overlapping chunks."""

from app.core.config import settings


def chunk_text(
    text: str,
    chunk_size: int = None,
    chunk_overlap: int = None,
    metadata: dict = None,
) -> list[dict]:
    chunk_size = chunk_size or settings.CHUNK_SIZE
    chunk_overlap = chunk_overlap or settings.CHUNK_OVERLAP
    metadata = metadata or {}

    text = text.strip()
    if not text:
        return []

    if len(text) <= chunk_size:
        return [{"text": text, "metadata": {**metadata, "chunk_index": 0}}]

    step = chunk_size - chunk_overlap
    chunks = []
    start = 0
    index = 0
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end].strip()
        if chunk:
            chunks.append({"text": chunk, "metadata": {**metadata, "chunk_index": index}})
            index += 1
        if end >= len(text):
            break
        start += step

    return chunks
