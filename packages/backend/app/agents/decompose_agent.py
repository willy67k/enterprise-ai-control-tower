"""Query decomposition node: one user turn → list of atomic sub-queries."""

from __future__ import annotations

import logging

from app.core.state import AgentState
from app.tools.llm.errors import LLMConfigurationError
from app.tools.llm.query_decompose import decompose_queries_structured_openai

logger = logging.getLogger(__name__)


def decompose_node(state: AgentState) -> dict:
    """Populate sub_queries and set query to the first sub-task."""
    original = (state.get("original_query") or state.get("query") or "").strip()
    role = state["role"]
    audit = list(state.get("audit_log") or [])

    if not original:
        audit.append("decompose: empty original; single empty task")
        return {
            "sub_queries": [""],
            "task_idx": 0,
            "query": "",
            "task_results": [],
            "audit_log": audit,
        }

    try:
        subs = decompose_queries_structured_openai(original, role=role)
    except LLMConfigurationError as e:
        logger.warning("Decompose (OpenAI): %s — fallback single task", e)
        subs = [original]
        audit.append("decompose: fallback_single (openai_config)")
    except Exception:
        logger.exception("Decompose (OpenAI) failed — fallback single task")
        subs = [original]
        audit.append("decompose: fallback_single (error)")

    if not subs:
        subs = [original]

    audit.append(f"decompose: {len(subs)} sub_queries")
    return {
        "sub_queries": subs,
        "task_idx": 0,
        "query": subs[0],
        "task_results": [],
        "audit_log": audit,
    }
