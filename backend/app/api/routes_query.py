"""API route: POST /query — answer an employee's question using the RAG pipeline."""

from fastapi import APIRouter

from app.core.rag_pipeline import answer_query
from app.models.schemas import QueryRequest, QueryResponse

router = APIRouter()


@router.post("/query", response_model=QueryResponse)
def query(request: QueryRequest) -> QueryResponse:
    result = answer_query(request.question)
    return QueryResponse(**result)
