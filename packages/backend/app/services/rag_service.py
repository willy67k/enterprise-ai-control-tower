"""Execute RAG: embed query → vector search → LLM answer."""

from __future__ import annotations

import logging
import uuid

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.document import DocumentChunk
from app.schemas.document import RagSourceSnippet
from app.tools.llm.errors import LLMConfigurationError
from app.tools.llm.invoke import chat as invoke_llm
from app.tools.rag.embedder import EmbeddingConfigurationError, embed_query
from app.tools.rag.prompt import build_rag_prompt
from app.tools.rag.retriever import retrieve_top_chunks

logger = logging.getLogger(__name__)

_PREVIEW_LEN = 280


def to_source_snippet(chunk: DocumentChunk) -> RagSourceSnippet:
    preview = chunk.content[:_PREVIEW_LEN]
    if len(chunk.content) > _PREVIEW_LEN:
        preview += "…"
    return RagSourceSnippet(
        document_id=chunk.document_id,
        chunk_index=chunk.chunk_index,
        preview=preview,
    )


def execute_rag(
    db: Session,
    *,
    owner_id: uuid.UUID,
    question: str,
    top_k: int,
    provider: str | None,
    model: str | None,
) -> tuple[str, str, str, list[DocumentChunk]]:
    """Return ``(reply, model_used, provider_used, chunks)``."""
    try:
        qvec = embed_query(question)
    except EmbeddingConfigurationError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(e)
        ) from e
    except Exception:
        logger.exception("Embedding failed for RAG query")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Embedding request failed",
        ) from None

    chunks = retrieve_top_chunks(
        db, owner_id=owner_id, query_embedding=qvec, top_k=top_k
    )
    prompt = build_rag_prompt(question, [c.content for c in chunks])

    try:
        reply, model_used, provider_used = invoke_llm(
            prompt, provider=provider, model=model
        )
    except LLMConfigurationError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(e)
        ) from e
    except Exception:
        logger.exception("LLM invocation failed for RAG")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="LLM request failed",
        ) from None

    return reply, model_used, provider_used, chunks
