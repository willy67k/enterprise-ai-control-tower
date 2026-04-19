"""Document upload, listing, and RAG query routes."""

from __future__ import annotations

import hashlib
import logging

from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    File,
    Form,
    HTTPException,
    UploadFile,
    status,
)
from fastapi.responses import JSONResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.middleware.auth import get_current_user
from app.config import get_settings
from app.models.document import Document
from app.models.rbac import User
from app.schemas.document import (
    DocumentListItem,
    DocumentListResponse,
    DocumentUploadResponse,
    RagQueryRequest,
    RagQueryResponse,
)
from app.services.db import get_db
from app.services.document_upload import process_upload
from app.services.rag_service import execute_rag, to_source_snippet
from app.tools.rag.loader import detect_source_type

logger = logging.getLogger(__name__)

router = APIRouter(tags=["documents"])


@router.post(
    "/documents/upload",
    response_model=DocumentUploadResponse,
    responses={
        200: {
            "description": "Same bytes already ingested for this user (deduplicated)."
        },
        202: {
            "description": "Accepted; text extraction and embedding run in background."
        },
    },
)
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    title: str | None = Form(None),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> JSONResponse:
    """Validate upload, then delegate dedup + ingest to ``process_upload``."""
    settings = get_settings()
    raw = await file.read()

    if len(raw) > settings.max_upload_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="File exceeds max_upload_bytes",
        )

    filename = file.filename or "upload"
    source_kind = detect_source_type(filename)
    if source_kind is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only .txt and .pdf files are supported",
        )

    doc_title = (title or "").strip() or filename

    return process_upload(
        db,
        user,
        raw=raw,
        filename=filename,
        source_kind=source_kind,
        doc_title=doc_title,
        content_sha256=hashlib.sha256(raw).hexdigest(),
        settings=settings,
        background_tasks=background_tasks,
    )


@router.get("/documents", response_model=DocumentListResponse)
def list_my_documents(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> DocumentListResponse:
    stmt = (
        select(Document)
        .where(Document.owner_id == user.id)
        .order_by(Document.created_at.desc())
    )
    rows = list(db.execute(stmt).scalars().all())
    return DocumentListResponse(
        documents=[
            DocumentListItem(
                id=r.id,
                title=r.title,
                source_type=r.source_type,
                ingestion_status=r.ingestion_status,
                created_at=r.created_at,
            )
            for r in rows
        ],
    )


@router.post("/documents/rag", response_model=RagQueryResponse)
def rag_ask(
    body: RagQueryRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> RagQueryResponse:
    """Retrieve top chunks for the user, then answer with the configured LLM."""
    reply, model_used, provider_used, chunks = execute_rag(
        db,
        owner_id=user.id,
        question=body.question,
        top_k=body.top_k,
        provider=body.provider,
        model=body.model,
    )
    return RagQueryResponse(
        reply=reply,
        model=model_used,
        provider=provider_used,
        sources=[to_source_snippet(c) for c in chunks],
    )
