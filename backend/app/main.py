"""FastAPI application entrypoint for the Sage — Employee AI Assistant backend."""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api import routes_documents, routes_feedback, routes_health, routes_ingest, routes_query
from app.core.config import settings
from app.utils.logger import get_logger

logger = get_logger(__name__)

app = FastAPI(title="Sage Employee AI Assistant API", version=settings.APP_VERSION)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8501", "http://frontend:8501"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(routes_health.router)
app.include_router(routes_ingest.router)
app.include_router(routes_query.router)
app.include_router(routes_documents.router)
app.include_router(routes_feedback.router)


@app.on_event("startup")
def log_llm_configuration() -> None:
    logger.info(
        "Local LLM configured: OLLAMA_BASE_URL=%s OLLAMA_MODEL=%s",
        settings.OLLAMA_BASE_URL,
        settings.OLLAMA_MODEL,
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.error("Unhandled exception on %s %s: %s", request.method, request.url.path, exc)
    return JSONResponse(status_code=500, content={"detail": "Internal server error."})
