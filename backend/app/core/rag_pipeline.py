"""End-to-end RAG pipeline: document ingestion and query answering with citations."""

import time

from app.core import llm_local, vectorstore
from app.core.chunking import chunk_text
from app.core.config import settings
from app.core.loaders import load_document
from app.utils.logger import get_logger

logger = get_logger(__name__)

_SYSTEM_PROMPT = (
    "You are an internal HR knowledge assistant. Answer the employee's question "
    "using ONLY the context provided below. If the answer is not contained in the "
    "context, clearly state that you don't have that information in the knowledge "
    "base rather than guessing. Keep your tone professional and HR-appropriate."
)

_NO_MATCH_ANSWER = "I couldn't find this in the knowledge base."


class DocumentIngestionError(Exception):
    """Raised when a document yields no extractable text."""


def ingest_document(file_path: str, original_filename: str) -> dict:
    text = load_document(file_path)
    if not text.strip():
        logger.error("Ingestion failed for '%s': no extractable text.", original_filename)
        raise DocumentIngestionError(
            f"No extractable text found in '{original_filename}'."
        )

    chunks = chunk_text(text, metadata={"source": original_filename})
    vectorstore.add_chunks(chunks)

    logger.info("Ingested '%s': %d chunks added.", original_filename, len(chunks))
    return {"filename": original_filename, "chunks_added": len(chunks)}


def _build_user_prompt(query: str, chunks: list[dict]) -> str:
    context = "\n\n".join(
        f"[{i}] {chunk['text']}" for i, chunk in enumerate(chunks, start=1)
    )
    return f"Context:\n{context}\n\nQuestion: {query}"


def _deduped_sources(chunks: list[dict]) -> list[dict]:
    sources = {}
    for chunk in chunks:
        metadata = chunk["metadata"]
        filename = metadata["source"]
        if filename not in sources:
            sources[filename] = {
                "filename": filename,
                "chunk_index": metadata["chunk_index"],
            }
    return list(sources.values())


def answer_query(query: str) -> dict:
    start = time.perf_counter()
    chunks = vectorstore.similarity_search(query, settings.TOP_K)
    chunks = [c for c in chunks if c["score"] >= settings.MIN_SIMILARITY_SCORE]

    if not chunks:
        latency = time.perf_counter() - start
        logger.info(
            "Query answered (no match): question_length=%d num_sources=0 latency=%.3fs",
            len(query),
            latency,
        )
        return {"answer": _NO_MATCH_ANSWER, "sources": []}

    user_prompt = _build_user_prompt(query, chunks)
    try:
        answer = llm_local.generate_answer(_SYSTEM_PROMPT, user_prompt)
    except llm_local.RAGGenerationError:
        logger.error("Query failed: question_length=%d num_sources=%d", len(query), len(chunks))
        raise

    sources = _deduped_sources(chunks)
    latency = time.perf_counter() - start
    logger.info(
        "Query answered: question_length=%d num_sources=%d latency=%.3fs",
        len(query),
        len(sources),
        latency,
    )

    return {"answer": answer, "sources": sources}
