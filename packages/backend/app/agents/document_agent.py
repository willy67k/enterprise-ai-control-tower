"""Document path: RAG over the current user's ingested chunks."""

from __future__ import annotations

import logging
import uuid

from langchain_core.runnables import RunnableConfig
from sqlalchemy.orm import Session

from app.core.state import AgentState
from app.models.document import DocumentChunk
from app.schemas.document import RagSourceSnippet
from app.services.rag_service import to_source_snippet
from app.tools.llm.errors import LLMConfigurationError
from app.tools.llm.invoke import chat as invoke_llm
from app.tools.rag.embedder import EmbeddingConfigurationError, embed_query
from app.tools.rag.prompt import build_rag_prompt
from app.tools.rag.retriever import retrieve_top_chunks

logger = logging.getLogger(__name__)


def document_node(state: AgentState, config: RunnableConfig) -> dict:
    cfg = config.get("configurable") or {}
    db: Session = cfg["db"]
    owner_id = uuid.UUID(str(cfg["owner_id"]))
    top_k = int(cfg.get("rag_top_k", 5))
    provider = cfg.get("llm_provider")
    model = cfg.get("llm_model")
    question = state["query"]

    audit = state["audit_log"] + ["document_agent: retrieve + answer"]

    try:
        qvec = embed_query(question)
    except EmbeddingConfigurationError as e:
        logger.warning("RAG embed config error: %s", e)
        return {
            "final_response": f"Document search is unavailable: {e}",
            "documents": [],
            "tool_result": {"error": "embedding_config", "detail": str(e)},
            "audit_log": audit + ["document_agent: embedding_config_error"],
        }
    except Exception:
        logger.exception("Embedding failed in document_agent")
        return {
            "final_response": "Document search failed while embedding the question.",
            "documents": [],
            "tool_result": {"error": "embedding_failed"},
            "audit_log": audit + ["document_agent: embedding_failed"],
        }

    chunks: list[DocumentChunk] = retrieve_top_chunks(
        db, owner_id=owner_id, query_embedding=qvec, top_k=top_k
    )
    snippets: list[dict] = [
        RagSourceSnippet(
            document_id=c.document_id,
            chunk_index=c.chunk_index,
            preview=to_source_snippet(c).preview,
        ).model_dump(mode="json")
        for c in chunks
    ]
    prompt = build_rag_prompt(question, [c.content for c in chunks])

    try:
        reply, model_used, provider_used = invoke_llm(
            prompt, provider=provider, model=model
        )
    except LLMConfigurationError as e:
        logger.warning("LLM config error in document_agent: %s", e)
        return {
            "final_response": f"Answer generation is unavailable: {e}",
            "documents": snippets,
            "tool_result": {
                "error": "llm_config",
                "detail": str(e),
                "sources": snippets,
            },
            "audit_log": audit + ["document_agent: llm_config_error"],
        }
    except Exception:
        logger.exception("LLM failed in document_agent")
        return {
            "final_response": "Answer generation failed after retrieval.",
            "documents": snippets,
            "tool_result": {"error": "llm_failed", "sources": snippets},
            "audit_log": audit + ["document_agent: llm_failed"],
        }

    return {
        "final_response": reply,
        "documents": snippets,
        "tool_result": {
            "model": model_used,
            "provider": provider_used,
            "sources": snippets,
        },
        "audit_log": audit + ["document_agent: ok"],
    }
