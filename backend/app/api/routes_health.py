"""API route: GET /health — service health and configuration status."""

from fastapi import APIRouter

from app.core import llm_local, vectorstore
from app.models.schemas import HealthResponse

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
def get_health() -> HealthResponse:
    return HealthResponse(
        status="ok",
        llm_backend_reachable=llm_local.is_reachable(),
        indexed_documents=len(vectorstore.list_sources()),
    )
