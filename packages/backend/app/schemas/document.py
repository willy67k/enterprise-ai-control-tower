from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from app.schemas.chat import LLMProviderEnum


class DocumentUploadResponse(BaseModel):
    id: UUID
    title: str | None = None
    source_type: str | None = None
    #: Populated when ingestion finished or duplicate ``ready``; omitted while ``pending``.
    chunk_count: int | None = None
    stored_filename: str | None = None
    content_sha256: str
    deduplicated: bool = False
    ingestion_status: str


class DocumentListItem(BaseModel):
    id: UUID
    title: str | None
    source_type: str | None
    ingestion_status: str
    created_at: datetime


class DocumentListResponse(BaseModel):
    documents: list[DocumentListItem]


class RagQueryRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=8000)
    top_k: int = Field(default=5, ge=1, le=20)
    provider: LLMProviderEnum | None = Field(
        default=None,
        description="LLM backend for the answer; omit for DEFAULT_LLM_PROVIDER.",
    )
    model: str | None = Field(default=None, description="Optional model id override.")


class RagSourceSnippet(BaseModel):
    document_id: UUID
    chunk_index: int
    preview: str


class RagQueryResponse(BaseModel):
    reply: str
    model: str
    provider: LLMProviderEnum
    sources: list[RagSourceSnippet]
