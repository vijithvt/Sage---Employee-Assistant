"""Pydantic request/response schemas for the backend API."""

from typing import Literal

from pydantic import BaseModel


class QueryRequest(BaseModel):
    question: str


class SourceRef(BaseModel):
    filename: str
    chunk_index: int


class FeedbackRequest(BaseModel):
    question: str
    answer: str
    rating: Literal["up", "down"]
    sources: list[SourceRef]


class QueryResponse(BaseModel):
    answer: str
    sources: list[SourceRef]


class IngestResponse(BaseModel):
    filename: str
    chunks_added: int


class DocumentListResponse(BaseModel):
    sources: list[str]


class HealthResponse(BaseModel):
    status: str
    version: str
    llm_backend_reachable: bool
    indexed_documents: int
