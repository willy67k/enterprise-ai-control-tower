"""Route user query to document, finance, or general path."""

from __future__ import annotations

import logging
from typing import Literal

from app.core.state import AgentState
from app.tools.llm.errors import LLMConfigurationError
from app.tools.llm.router_intent import classify_intent_structured_openai

logger = logging.getLogger(__name__)

Intent = Literal["document", "finance", "general"]


def classify_intent(query: str, *, role: str) -> Intent:
    """Semantic intent via GPT-4o-mini structured output; safe fallback if OpenAI fails."""
    q = query.strip()
    if not q:
        return "general"
    try:
        return classify_intent_structured_openai(q, role=role)
    except LLMConfigurationError as e:
        logger.warning("Intent router (OpenAI): %s", e)
        return "document" if role == "viewer" else "general"
    except Exception:
        logger.exception("Intent router (OpenAI) failed")
        return "document" if role == "viewer" else "general"


def router_node(state: AgentState) -> dict:
    intent = classify_intent(state["query"], role=state["role"])
    log = state["audit_log"] + [f"router: intent={intent} (openai_structured)"]
    q = state["query"]
    logger.debug("router intent=%s query_preview=%s", intent, (q or "")[:120])
    return {"intent": intent, "audit_log": log}
