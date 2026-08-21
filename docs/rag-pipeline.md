# How Sage's RAG Pipeline Works

This explains the pipeline in plain engineering terms, step by step, for
anyone new to Retrieval-Augmented Generation. Each step names the actual
file responsible for it in this codebase, so you can jump straight to the
code.

```
Load → Clean → Chunk → Embed → Store → Retrieve → Build prompt → Generate → Return answer + sources
```

## The steps

### 1. Load

A document (PDF, DOCX, TXT, or Markdown) is read and its raw text is
extracted.

**File:** `backend/app/core/loaders.py` — `load_document()` picks the
right extraction function by file extension (`load_pdf`, `load_docx`,
`load_text`).

### 2. Clean

Raw extracted text is messy — extra whitespace, blank lines, inconsistent
line breaks. It gets normalized before anything else touches it.

**File:** `backend/app/core/loaders.py` — `_clean_text()`, called
internally by every loader function above.

### 3. Chunk

Long documents can't be fed to an embedding model or an LLM whole, so the
cleaned text is split into overlapping windows. The overlap (`CHUNK_OVERLAP`)
exists so that a sentence sitting on a chunk boundary doesn't lose context
that would only be in the neighboring chunk.

**File:** `backend/app/core/chunking.py` — `chunk_text()`. Defaults:
`CHUNK_SIZE=800`, `CHUNK_OVERLAP=120` (both in characters, not tokens).

### 4. Embed

Each chunk of text is converted into a vector (a list of numbers) that
captures its meaning, using a local embedding model.

**File:** `backend/app/core/embeddings.py` — `embed_texts()` (batch, used
during ingestion) and `embed_query()` (single string, used at query time).
Model: `sentence-transformers/all-MiniLM-L6-v2` by default, fully local.

### 5. Store

Chunk text, its embedding, and metadata (source filename, chunk index) are
saved into the vector database.

**File:** `backend/app/core/vectorstore.py` — `add_chunks()`, backed by a
single ChromaDB collection (`employee_kb`), persisted to a Docker volume.

### 6. Retrieve

When a question comes in, it's embedded the same way documents were, and
the vector store returns the most similar stored chunks, ranked by score.

**File:** `backend/app/core/vectorstore.py` — `similarity_search()`,
called from `backend/app/core/rag_pipeline.py` — `answer_query()`.

### 7. Build prompt

The retrieved chunks are numbered and assembled into a `Context:` block,
followed by the employee's actual question, plus a system prompt
instructing the model to answer only from that context.

**File:** `backend/app/core/rag_pipeline.py` — `_build_user_prompt()` and
the module-level `_SYSTEM_PROMPT`.

### 8. Generate

The assembled prompt is sent to the local LLM (via Ollama), which produces
the answer text.

**File:** `backend/app/core/llm_local.py` — `generate_answer()`.

### 9. Return answer + sources

The generated answer is paired with a deduplicated list of the source
documents it was grounded in, and returned to the frontend for display.

**File:** `backend/app/core/rag_pipeline.py` — `_deduped_sources()` and
`answer_query()`'s return value; rendered by
`frontend/components/source_display.py`.

---

## Known limitations

These are real, current limitations — documented honestly rather than
fixed prematurely. Each one is a candidate lesson for a later course phase
(mostly V0.2 — RAG Engineering).

- **Character-based chunking.** `CHUNK_SIZE`/`CHUNK_OVERLAP` count
  characters, not model tokens, so they don't map precisely onto the LLM's
  actual context window usage.
- **Limited citation metadata.** A source citation is just
  `{filename, chunk_index}` — no page number, section heading, or excerpt.
- **No page-aware PDF metadata.** PDF loading concatenates all pages into
  one text blob before chunking; a citation can't currently point to "page 4."
- **Dense retrieval only.** Similarity search is purely embedding-based —
  no keyword/BM25 component, so exact-term matches (e.g. a policy code or
  acronym) aren't specially weighted.
- **No reranker.** Retrieved chunks are used in the order ChromaDB returns
  them; there's no second-pass model to re-score and reorder them.
- **Simple similarity threshold.** `MIN_SIMILARITY_SCORE` is a single
  global cutoff, hand-calibrated against one embedding model and one small
  document set — not adaptive, not validated against a real eval set.
- **No formal evaluation dataset.** Retrieval and answer quality have been
  checked by manually asking questions and reading the answers, not by a
  repeatable, scored evaluation suite.
- **Conversation history lives only in the frontend session.** Streamlit's
  `st.session_state` holds chat history in the browser session; the
  backend is stateless per request and has no memory of prior turns.
- **Direct coupling to Ollama.** `llm_local.py` is written against the
  Ollama Python client specifically, not behind a provider-agnostic
  interface — swapping providers today means editing that module directly,
  not flipping a config flag. (See `docs/architecture.md` → "Where Sage is
  going" for the planned direction on configurable providers.)
