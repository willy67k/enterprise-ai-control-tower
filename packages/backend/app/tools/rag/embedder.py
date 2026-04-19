"""OpenAI embedding calls (1536-dim text-embedding-3-small)."""

from __future__ import annotations

from langchain_openai import OpenAIEmbeddings

from app.config import get_settings


class EmbeddingConfigurationError(RuntimeError):
    """Missing or invalid embedding configuration."""


def _client() -> OpenAIEmbeddings:
    settings = get_settings()
    if not (settings.openai_api_key or "").strip():
        raise EmbeddingConfigurationError(
            "OPENAI_API_KEY is required for embeddings; add it to .env",
        )
    return OpenAIEmbeddings(
        api_key=settings.openai_api_key,
        model=settings.openai_embedding_model,
    )


def embed_documents(texts: list[str], *, batch_size: int = 64) -> list[list[float]]:
    """Embed many strings in batches (avoids huge single requests)."""
    if not texts:
        return []
    if batch_size < 1:
        raise ValueError("batch_size must be at least 1")
    client = _client()
    out: list[list[float]] = []
    for i in range(0, len(texts), batch_size):
        batch = texts[i : i + batch_size]
        out.extend(client.embed_documents(batch))
    return out


def embed_query(text: str) -> list[float]:
    """Embed a single query string."""
    return _client().embed_query(text)
