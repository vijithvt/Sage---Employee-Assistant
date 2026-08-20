"""API route: POST /ingest — upload and index a document into the knowledge base."""

import tempfile
from pathlib import Path

from fastapi import APIRouter, HTTPException, UploadFile

from app.core.config import settings
from app.core.rag_pipeline import DocumentIngestionError, ingest_document
from app.models.schemas import IngestResponse

router = APIRouter()

_ALLOWED_EXTENSIONS = {".pdf", ".docx", ".txt", ".md"}


@router.post("/ingest", response_model=IngestResponse)
async def ingest(file: UploadFile) -> IngestResponse:
    extension = Path(file.filename).suffix.lower()
    if extension not in _ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type '{extension}'. Allowed: {', '.join(sorted(_ALLOWED_EXTENSIONS))}",
        )

    contents = await file.read()
    max_bytes = settings.MAX_UPLOAD_MB * 1024 * 1024
    if len(contents) > max_bytes:
        raise HTTPException(
            status_code=400,
            detail=f"File exceeds the maximum upload size of {settings.MAX_UPLOAD_MB}MB.",
        )

    with tempfile.NamedTemporaryFile(suffix=extension, delete=False) as tmp:
        tmp.write(contents)
        tmp_path = tmp.name

    try:
        summary = ingest_document(tmp_path, file.filename)
    except DocumentIngestionError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    finally:
        Path(tmp_path).unlink(missing_ok=True)

    return IngestResponse(**summary)
