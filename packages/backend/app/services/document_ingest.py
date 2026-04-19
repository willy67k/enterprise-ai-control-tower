"""Background ingestion: extract text, chunk, embed, persist chunks."""

from __future__ import annotations

import logging
import uuid
from pathlib import Path

from sqlalchemy import delete, func, select
from sqlalchemy.orm import Session

from app.config import get_settings
from app.models.document import Document, DocumentChunk
from app.services.db import SessionLocal
from app.tools.rag.chunker import chunk_text
from app.tools.rag.embedder import EmbeddingConfigurationError, embed_documents
from app.tools.rag.loader import extract_text

logger = logging.getLogger(__name__)


def run_document_ingestion(
    document_id: uuid.UUID,
    upload_path: str | Path,
    original_filename: str,
) -> None:
    """Run outside request scope; uses a fresh DB session."""
    settings = get_settings()
    db = SessionLocal()
    try:
        doc = db.get(Document, document_id)
        if doc is None:
            logger.error("Ingestion: document %s not found", document_id)
            return

        path = Path(upload_path)
        if not path.is_file():
            doc.ingestion_status = "failed"
            doc.ingestion_error = f"Upload file missing: {path}"
            db.commit()
            return

        raw = path.read_bytes()
        try:
            text, source_kind = extract_text(original_filename, raw)
        except ValueError as e:
            doc.ingestion_status = "failed"
            doc.ingestion_error = str(e)
            db.commit()
            return

        doc.content = text
        doc.source_type = source_kind
        db.flush()

        chunks = chunk_text(
            text,
            chunk_size=settings.rag_chunk_size,
            overlap=settings.rag_chunk_overlap,
        )
        if not chunks:
            doc.ingestion_status = "failed"
            doc.ingestion_error = "Document produced no chunks after processing"
            db.commit()
            return

        try:
            vectors = embed_documents(chunks)
        except EmbeddingConfigurationError as e:
            doc.ingestion_status = "failed"
            doc.ingestion_error = str(e)
            db.commit()
            return
        except Exception:
            logger.exception("Embedding failed for document %s", document_id)
            doc.ingestion_status = "failed"
            doc.ingestion_error = "Embedding request failed"
            db.commit()
            return

        if len(vectors) != len(chunks):
            doc.ingestion_status = "failed"
            doc.ingestion_error = "Embedding count mismatch"
            db.commit()
            return

        db.execute(delete(DocumentChunk).where(DocumentChunk.document_id == doc.id))
        for idx, (piece, vec) in enumerate(zip(chunks, vectors, strict=True)):
            db.add(
                DocumentChunk(
                    document_id=doc.id,
                    chunk_index=idx,
                    content=piece,
                    embedding=vec,
                    metadata_={"original_filename": original_filename},
                )
            )

        doc.ingestion_status = "ready"
        doc.ingestion_error = None
        db.commit()
    except Exception:
        logger.exception("Ingestion crashed for document %s", document_id)
        db.rollback()
        try:
            doc = db.get(Document, document_id)
            if doc is not None:
                doc.ingestion_status = "failed"
                doc.ingestion_error = "Unexpected ingestion error"
                db.commit()
        except Exception:
            logger.exception("Could not persist failed status for %s", document_id)
            db.rollback()
    finally:
        db.close()


def count_chunks_for_document(db_session: Session, document_id: uuid.UUID) -> int:
    stmt = (
        select(func.count())
        .select_from(DocumentChunk)
        .where(DocumentChunk.document_id == document_id)
    )
    return int(db_session.execute(stmt).scalar_one())
