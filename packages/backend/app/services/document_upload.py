"""Business logic for document upload: dedup, file persistence, ingest queue."""

from __future__ import annotations

import uuid
from pathlib import Path

from fastapi import BackgroundTasks, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.config import Settings
from app.models.document import Document
from app.models.rbac import User
from app.schemas.document import DocumentUploadResponse
from app.services.document_ingest import (
    count_chunks_for_document,
    run_document_ingestion,
)


# ---------------------------------------------------------------------------
# File path helpers
# ---------------------------------------------------------------------------


def stored_filename(doc_id: uuid.UUID, source_type: str | None) -> str:
    ext = ".pdf" if source_type == "pdf" else ".txt"
    return f"{doc_id}{ext}"


def _write_file(
    doc_id: uuid.UUID, source_type: str, raw: bytes, settings: Settings
) -> Path:
    upload_root = Path(settings.upload_dir)
    upload_root.mkdir(parents=True, exist_ok=True)
    path = upload_root / stored_filename(doc_id, source_type)
    path.write_bytes(raw)
    return path


def _enqueue(
    doc: Document, path: Path, filename: str, background_tasks: BackgroundTasks
) -> None:
    background_tasks.add_task(
        run_document_ingestion, doc.id, str(path.resolve()), filename
    )


# ---------------------------------------------------------------------------
# Response builders
# ---------------------------------------------------------------------------


def _pending_response(doc: Document, content_sha256: str) -> DocumentUploadResponse:
    return DocumentUploadResponse(
        id=doc.id,
        title=doc.title,
        source_type=doc.source_type,
        chunk_count=None,
        stored_filename=stored_filename(doc.id, doc.source_type),
        content_sha256=content_sha256,
        deduplicated=False,
        ingestion_status="pending",
    )


def _ready_response(
    doc: Document, db: Session, content_sha256: str
) -> DocumentUploadResponse:
    return DocumentUploadResponse(
        id=doc.id,
        title=doc.title,
        source_type=doc.source_type,
        chunk_count=count_chunks_for_document(db, doc.id),
        stored_filename=stored_filename(doc.id, doc.source_type),
        content_sha256=content_sha256,
        deduplicated=True,
        ingestion_status="ready",
    )


def _as_json(body: DocumentUploadResponse, *, http_status: int) -> JSONResponse:
    return JSONResponse(status_code=http_status, content=body.model_dump(mode="json"))


# ---------------------------------------------------------------------------
# Dedup helpers
# ---------------------------------------------------------------------------


def _query_by_hash(
    db: Session, owner_id: uuid.UUID, content_sha256: str
) -> Document | None:
    return db.execute(
        select(Document).where(
            Document.owner_id == owner_id,
            Document.content_hash == content_sha256,
        )
    ).scalar_one_or_none()


def _respond_to_duplicate(
    doc: Document, db: Session, content_sha256: str
) -> JSONResponse:
    if doc.ingestion_status == "ready":
        return _as_json(
            _ready_response(doc, db, content_sha256), http_status=status.HTTP_200_OK
        )
    return _as_json(
        _pending_response(doc, content_sha256), http_status=status.HTTP_202_ACCEPTED
    )


def _handle_existing(
    existing: Document,
    db: Session,
    content_sha256: str,
    source_kind: str,
    doc_title: str | None,
    raw: bytes,
    settings: Settings,
    filename: str,
    background_tasks: BackgroundTasks,
) -> JSONResponse:
    """Resolve an already-known document (ready / pending / failed)."""
    if existing.ingestion_status == "ready":
        return _as_json(
            _ready_response(existing, db, content_sha256),
            http_status=status.HTTP_200_OK,
        )

    if existing.ingestion_status == "pending":
        return _as_json(
            _pending_response(existing, content_sha256),
            http_status=status.HTTP_202_ACCEPTED,
        )

    # failed → reset and retry
    existing.title = doc_title
    existing.ingestion_status = "pending"
    existing.ingestion_error = None
    existing.source_type = source_kind
    db.flush()
    path = _write_file(existing.id, source_kind, raw, settings)
    db.commit()
    _enqueue(existing, path, filename, background_tasks)
    return _as_json(
        _pending_response(existing, content_sha256),
        http_status=status.HTTP_202_ACCEPTED,
    )


def _handle_integrity_error(
    db: Session,
    user_id: uuid.UUID,
    content_sha256: str,
    context: str,
) -> Document:
    """Re-query after an IntegrityError; raise 409 if the row is still missing."""
    dup = _query_by_hash(db, user_id, content_sha256)
    if dup is None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Document conflict ({context}); retry upload",
        )
    return dup


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------


def process_upload(
    db: Session,
    user: User,
    *,
    raw: bytes,
    filename: str,
    source_kind: str,
    doc_title: str | None,
    content_sha256: str,
    settings: Settings,
    background_tasks: BackgroundTasks,
) -> JSONResponse:
    """Dedup check → create document row → write file → enqueue background ingest."""
    existing = _query_by_hash(db, user.id, content_sha256)
    if existing is not None:
        return _handle_existing(
            existing,
            db,
            content_sha256,
            source_kind,
            doc_title,
            raw,
            settings,
            filename,
            background_tasks,
        )

    doc = Document(
        owner_id=user.id,
        title=doc_title,
        content="",
        source_type=source_kind,
        content_hash=content_sha256,
        ingestion_status="pending",
    )
    db.add(doc)
    try:
        db.flush()
    except IntegrityError:
        db.rollback()
        dup = _handle_integrity_error(db, user.id, content_sha256, "flush")
        return _respond_to_duplicate(dup, db, content_sha256)

    path = _write_file(doc.id, source_kind, raw, settings)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        dup = _handle_integrity_error(db, user.id, content_sha256, "commit")
        return _respond_to_duplicate(dup, db, content_sha256)

    _enqueue(doc, path, filename, background_tasks)
    return _as_json(
        _pending_response(doc, content_sha256), http_status=status.HTTP_202_ACCEPTED
    )
