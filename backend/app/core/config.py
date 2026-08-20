"""Application settings loaded from environment variables / .env file."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Application metadata
    APP_VERSION: str = "0.1.0"

    # Local LLM (Ollama) — see docs/architecture.md for the generation flow
    OLLAMA_BASE_URL: str = "http://ollama:11434"
    OLLAMA_MODEL: str = "qwen2.5:1.5b"

    # Embeddings (sentence-transformers, always local)
    EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"

    # ChromaDB persistence
    CHROMA_PERSIST_DIR: str = "/app/data/chroma_db"

    # Chunking (character-based — see docs/rag-pipeline.md for limitations)
    CHUNK_SIZE: int = 800
    CHUNK_OVERLAP: int = 120

    # Retrieval
    TOP_K: int = 5
    # Chunks scoring below this are discarded before the LLM sees them —
    # this is the system's actual grounding guard, since small local models
    # are unreliable at self-policing "only answer from context" prompts.
    # See docs/rag-pipeline.md "Known limitations" for more on this.
    MIN_SIMILARITY_SCORE: float = -0.5

    # Ingestion
    MAX_UPLOAD_MB: int = 20

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
