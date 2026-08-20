"""Unit tests for backend/app/core/rag_pipeline.py."""

from unittest.mock import patch

from app.core import rag_pipeline


def test_answer_query_grounded_path():
    retrieved_chunks = [
        {
            "text": "Employees get 20 days of annual leave.",
            "metadata": {"source": "leave_policy.md", "chunk_index": 0},
            "score": 0.9,
        },
        {
            "text": "Leave requests must be submitted 2 weeks in advance.",
            "metadata": {"source": "leave_policy.md", "chunk_index": 1},
            "score": 0.8,
        },
        {
            "text": "The IT helpdesk is open 9-5.",
            "metadata": {"source": "it_helpdesk_sop.md", "chunk_index": 0},
            "score": 0.6,
        },
    ]

    with patch.object(rag_pipeline.vectorstore, "similarity_search", return_value=retrieved_chunks) as mock_search, \
         patch.object(rag_pipeline.llm_local, "generate_answer", return_value="You get 20 days of leave.") as mock_generate:
        result = rag_pipeline.answer_query("How many leave days do I get?")

    mock_search.assert_called_once()
    mock_generate.assert_called_once()

    assert result["answer"] == "You get 20 days of leave."
    assert result["sources"] == [
        {"filename": "leave_policy.md", "chunk_index": 0},
        {"filename": "it_helpdesk_sop.md", "chunk_index": 0},
    ]


def test_answer_query_no_match_path():
    with patch.object(rag_pipeline.vectorstore, "similarity_search", return_value=[]) as mock_search, \
         patch.object(rag_pipeline.llm_local, "generate_answer") as mock_generate:
        result = rag_pipeline.answer_query("What is the meaning of life?")

    mock_search.assert_called_once()
    mock_generate.assert_not_called()

    assert result["answer"] == "I couldn't find this in the knowledge base."
    assert result["sources"] == []


def test_answer_query_below_similarity_threshold_skips_llm():
    # All retrieved chunks score below settings.MIN_SIMILARITY_SCORE, so the
    # LLM should never be called (guards against small local models
    # hallucinating an answer to an out-of-scope question).
    irrelevant_chunks = [
        {
            "text": "The IT helpdesk is open 9-5.",
            "metadata": {"source": "it_helpdesk_sop.md", "chunk_index": 0},
            "score": -0.95,
        },
    ]

    with patch.object(rag_pipeline.vectorstore, "similarity_search", return_value=irrelevant_chunks) as mock_search, \
         patch.object(rag_pipeline.llm_local, "generate_answer") as mock_generate:
        result = rag_pipeline.answer_query("What is the capital of France?")

    mock_search.assert_called_once()
    mock_generate.assert_not_called()

    assert result["answer"] == "I couldn't find this in the knowledge base."
    assert result["sources"] == []
