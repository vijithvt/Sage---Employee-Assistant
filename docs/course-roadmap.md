# Sage — Course Roadmap

Sage evolves progressively across the course, from a minimal working RAG
app to a full agentic assistant exposed over MCP. Each version is a
self-contained milestone — the app should run at the end of every stage.

This is a **plan**, not a changelog. Nothing beyond V0.1 is implemented
yet. See [Repository Checkpoints](../README.md#repository-checkpoints) in
the README for how each version will be tagged once it lands.

---

## V0.1 — RAG MVP *(current)*

- Streamlit chat UI
- FastAPI backend
- ChromaDB vector store
- Ollama local LLM generation
- Document ingestion (PDF/DOCX/TXT/Markdown)
- Source citations
- Thumbs-up/down feedback capture

## V0.2 — RAG Engineering

- Richer chunk metadata (page numbers, section headers)
- Page-aware citations for PDFs
- Improved chunking strategy (beyond fixed-size character windows)
- Retrieval evaluation (a real eval set, not just spot-checking)
- Better similarity scoring / threshold calibration
- Hybrid retrieval (dense + keyword)
- Reranking

## V0.3 — Product UI

- React + TypeScript + Vite + Tailwind frontend, replacing Streamlit
- Streaming responses (token-by-token, not a single blocking call)
- Proper chat history UI
- Source cards (richer than the current text expander)
- Knowledge-base management UI (upload/list/remove, carried over from
  Streamlit but rebuilt)

## V0.4 — AI Tools

- Policy search as a callable tool (distinct from the default RAG path)
- Employee directory lookup
- Leave balance lookup
- IT ticket creation

## V0.5 — Agent

- LangGraph-based orchestration
- Tool routing (the agent decides RAG vs. a specific tool vs. both)
- Conversation state across turns
- Human-in-the-loop approval for sensitive actions
- Persistence of agent state

## V0.6 — MCP

- Expose Sage's tools through the Model Context Protocol
- Allow external MCP-compatible clients to connect to Sage's tools

## V1.0 — Production Course Version

- Fully Dockerized full stack (frontend, backend, agent, tools)
- Comprehensive test coverage
- Retrieval/agent evaluation suite
- Structured logging throughout
- Security discussion (auth, rate limiting, secrets handling)
- Polished, learner-facing documentation
