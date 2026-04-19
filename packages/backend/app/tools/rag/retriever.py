"""Vector similarity search over document_chunks (pgvector)."""

from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.document import Document, DocumentChunk


def retrieve_top_chunks(
    db: Session,
    *,
    owner_id: uuid.UUID,
    query_embedding: list[float],
    top_k: int = 5,
) -> list[DocumentChunk]:
    """Cosine distance ordering; only chunks owned by ``owner_id`` documents."""
    if top_k < 1:
        raise ValueError("top_k must be at least 1")

    distance = DocumentChunk.embedding.cosine_distance(query_embedding)
    stmt = (
        select(DocumentChunk)
        .join(Document, DocumentChunk.document_id == Document.id)
        .where(
            Document.owner_id == owner_id,
            Document.ingestion_status == "ready",
        )
        .order_by(distance)
        .limit(top_k)
    )
    return list(db.execute(stmt).scalars().all())
