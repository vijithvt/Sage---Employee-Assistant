"""API routes: GET /documents and DELETE /documents/{filename} — manage indexed sources."""

from fastapi import APIRouter

from app.core import vectorstore
from app.models.schemas import DocumentListResponse

router = APIRouter()


@router.get("/documents", response_model=DocumentListResponse)
def list_documents() -> DocumentListResponse:
    return DocumentListResponse(sources=vectorstore.list_sources())


@router.delete("/documents/{filename}")
def delete_document(filename: str) -> dict:
    vectorstore.delete_source(filename)
    return {"detail": f"Removed '{filename}' from the knowledge base."}
