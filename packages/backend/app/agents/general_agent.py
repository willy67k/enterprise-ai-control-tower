"""General path: single LLM turn without RAG."""

from __future__ import annotations

import logging

from langchain_core.runnables import RunnableConfig

from app.core.state import AgentState
from app.tools.llm.errors import LLMConfigurationError
from app.tools.llm.invoke import chat as invoke_llm

logger = logging.getLogger(__name__)


def general_node(state: AgentState, config: RunnableConfig) -> dict:
    cfg = config.get("configurable") or {}
    provider = cfg.get("llm_provider")
    model = cfg.get("llm_model")
    audit = state["audit_log"] + ["general_agent: direct_llm"]

    try:
        reply, model_used, provider_used = invoke_llm(
            state["query"], provider=provider, model=model
        )
    except LLMConfigurationError as e:
        logger.warning("LLM config error in general_agent: %s", e)
        return {
            "final_response": f"Chat is unavailable: {e}",
            "tool_result": {"error": "llm_config", "detail": str(e)},
            "audit_log": audit + ["general_agent: llm_config_error"],
        }
    except Exception:
        logger.exception("LLM failed in general_agent")
        return {
            "final_response": "The model request failed.",
            "tool_result": {"error": "llm_failed"},
            "audit_log": audit + ["general_agent: llm_failed"],
        }

    return {
        "final_response": reply,
        "tool_result": {"model": model_used, "provider": provider_used},
        "audit_log": audit + ["general_agent: ok"],
    }
