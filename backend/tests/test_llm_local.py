"""Unit tests for backend/app/core/llm_local.py."""

from types import SimpleNamespace
from unittest.mock import patch

import pytest

from app.core import llm_local


@pytest.fixture(autouse=True)
def _reset_model_ready():
    llm_local._model_ready = False
    yield
    llm_local._model_ready = False


def _models_response(model_names):
    return SimpleNamespace(models=[SimpleNamespace(model=name) for name in model_names])


def test_generate_answer_success_when_model_already_present():
    chat_response = SimpleNamespace(message=SimpleNamespace(content="You get 20 days of leave."))

    with patch.object(llm_local._client, "list", return_value=_models_response([llm_local.settings.OLLAMA_MODEL])) as mock_list, \
         patch.object(llm_local._client, "pull") as mock_pull, \
         patch.object(llm_local._client, "chat", return_value=chat_response) as mock_chat:
        answer = llm_local.generate_answer("system prompt", "user prompt")

    assert answer == "You get 20 days of leave."
    mock_list.assert_called_once()
    mock_pull.assert_not_called()
    mock_chat.assert_called_once()


def test_generate_answer_pulls_model_when_missing():
    chat_response = SimpleNamespace(message=SimpleNamespace(content="Answer."))

    with patch.object(llm_local._client, "list", return_value=_models_response([])) as mock_list, \
         patch.object(llm_local._client, "pull", return_value=[{"status": "success"}]) as mock_pull, \
         patch.object(llm_local._client, "chat", return_value=chat_response):
        answer = llm_local.generate_answer("system prompt", "user prompt")

    assert answer == "Answer."
    mock_list.assert_called_once()
    mock_pull.assert_called_once_with(llm_local.settings.OLLAMA_MODEL, stream=True)


def test_generate_answer_wraps_connection_failure():
    with patch.object(llm_local._client, "list", side_effect=ConnectionError("refused")):
        with pytest.raises(llm_local.RAGGenerationError):
            llm_local.generate_answer("system prompt", "user prompt")


def test_generate_answer_wraps_chat_failure():
    with patch.object(llm_local._client, "list", return_value=_models_response([llm_local.settings.OLLAMA_MODEL])), \
         patch.object(llm_local._client, "chat", side_effect=RuntimeError("boom")):
        with pytest.raises(llm_local.RAGGenerationError):
            llm_local.generate_answer("system prompt", "user prompt")


def test_is_reachable_true_and_false():
    with patch.object(llm_local._client, "list", return_value=_models_response([])):
        assert llm_local.is_reachable() is True

    with patch.object(llm_local._client, "list", side_effect=ConnectionError("refused")):
        assert llm_local.is_reachable() is False
