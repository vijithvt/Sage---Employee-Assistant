"""Wrapper around a local Ollama server for LLM answer generation."""

import ollama

from app.core.config import settings
from app.utils.logger import get_logger

logger = get_logger(__name__)

_client = ollama.Client(host=settings.OLLAMA_BASE_URL)
_model_ready = False


class RAGGenerationError(Exception):
    """Raised when the local LLM fails to generate an answer."""


def is_reachable() -> bool:
    try:
        _client.list()
        return True
    except Exception:
        return False


def _ensure_model_available() -> None:
    global _model_ready
    if _model_ready:
        return

    try:
        local_models = {model.model for model in _client.list().models}
    except Exception as exc:
        raise RAGGenerationError(
            f"Could not reach the local LLM service at {settings.OLLAMA_BASE_URL}. "
            "Is the 'ollama' container running?"
        ) from exc

    if settings.OLLAMA_MODEL not in local_models:
        logger.info("Pulling local model '%s' (first run only)...", settings.OLLAMA_MODEL)
        try:
            for progress in _client.pull(settings.OLLAMA_MODEL, stream=True):
                status = progress.get("status")
                if status:
                    logger.info("Ollama pull '%s': %s", settings.OLLAMA_MODEL, status)
        except Exception as exc:
            raise RAGGenerationError(
                f"Failed to pull local model '{settings.OLLAMA_MODEL}': {exc}"
            ) from exc
        logger.info("Local model '%s' is ready.", settings.OLLAMA_MODEL)

    _model_ready = True


def generate_answer(system_prompt: str, user_prompt: str, temperature: float = 0.2) -> str:
    _ensure_model_available()

    try:
        response = _client.chat(
            model=settings.OLLAMA_MODEL,
            options={"temperature": temperature},
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )
    except RAGGenerationError:
        raise
    except Exception as exc:
        logger.error("Local LLM request failed: %s", exc)
        raise RAGGenerationError(
            f"Could not reach the local LLM service. Is the 'ollama' container running? ({exc})"
        ) from exc

    return response.message.content
