"""Persistent ChromaDB vector store wrapper for the employee knowledge base."""

import hashlib

import chromadb

from app.core.config import settings
from app.core.embeddings import embed_query, embed_texts

_client = chromadb.PersistentClient(path=settings.CHROMA_PERSIST_DIR)
_collection = _client.get_or_create_collection("employee_kb")


def _chunk_id(source: str, chunk_index: int) -> str:
    return hashlib.sha256(f"{source}::{chunk_index}".encode("utf-8")).hexdigest()


def add_chunks(chunks: list[dict]) -> None:
    if not chunks:
        return

    texts = [chunk["text"] for chunk in chunks]
    metadatas = [chunk["metadata"] for chunk in chunks]
    ids = [_chunk_id(meta["source"], meta["chunk_index"]) for meta in metadatas]
    embeddings = embed_texts(texts)

    _collection.upsert(ids=ids, embeddings=embeddings, documents=texts, metadatas=metadatas)


def similarity_search(query: str, k: int) -> list[dict]:
    results = _collection.query(query_embeddings=[embed_query(query)], n_results=k)

    documents = results.get("documents") or [[]]
    metadatas = results.get("metadatas") or [[]]
    distances = results.get("distances") or [[]]

    return [
        {"text": text, "metadata": metadata, "score": 1 - distance}
        for text, metadata, distance in zip(documents[0], metadatas[0], distances[0])
    ]


def list_sources() -> list[str]:
    records = _collection.get(include=["metadatas"])
    sources = {meta["source"] for meta in records.get("metadatas", []) if meta.get("source")}
    return sorted(sources)


def delete_source(filename: str) -> None:
    _collection.delete(where={"source": filename})
