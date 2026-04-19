"""Route user intent via OpenAI structured output (gpt-4o-mini, JSON schema)."""

from __future__ import annotations

import logging
from typing import Literal

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field

from app.config import get_settings
from app.tools.llm.errors import LLMConfigurationError

logger = logging.getLogger(__name__)

# Dedicated model for semantic routing (explicit per product requirement).
ROUTER_INTENT_MODEL = "gpt-4o-mini"


class RouterIntentStructured(BaseModel):
    """OpenAI structured output payload (strict JSON schema)."""

    intent: Literal["document", "finance", "general"] = Field(
        description=(
            "document: internal docs, policies, handbooks, uploads, or answers that "
            "should be grounded in company knowledge (RAG). "
            "finance: revenue, profit, KPIs, budgets, margins, cash flow, accounting, "
            "or quantitative business/financial performance. "
            "general: greetings, chitchat, open-domain tasks, or anything not clearly "
            "document- or finance-specific."
        )
    )


_SYSTEM = """You classify user messages for an enterprise assistant. Pick exactly one intent:

- document — Questions about internal documents, policies, procedures, handbooks, or anything that should be answered from company-owned materials (retrieval / RAG).

- finance — Financial or business-performance analysis: revenue, costs, profit, KPIs, budgets, margins, cash flow, accounting, forecasting, or similar numeric/commercial topics.

- general — Greetings, small talk, generic knowledge, creative writing, or tasks that are not clearly tied to internal documents or finance.

When unsure, use the provided user_role. If user_role is "viewer", lean toward document when the user might need internal sources; choose finance only when the question clearly concerns money, metrics, or financial performance.

You must output only fields allowed by the schema; intent must be one of: document, finance, general."""


def classify_intent_structured_openai(
    query: str,
    *,
    role: str,
) -> Literal["document", "finance", "general"]:
    """Call GPT-4o-mini with structured output (JSON schema)."""
    settings = get_settings()
    key = (settings.openai_api_key or "").strip()
    if not key:
        raise LLMConfigurationError(
            "OPENAI_API_KEY is not set; semantic intent routing requires OpenAI",
        )

    llm = ChatOpenAI(
        api_key=key,
        model=ROUTER_INTENT_MODEL,
        temperature=0,
    )
    structured = llm.with_structured_output(
        RouterIntentStructured,
        method="json_schema",
        strict=True,
    )
    messages = [
        SystemMessage(content=_SYSTEM),
        HumanMessage(content=f"user_role: {role}\n\nuser_query:\n{query}"),
    ]
    out: RouterIntentStructured = structured.invoke(messages)
    logger.debug("router_intent_structured intent=%s", out.intent)
    return out.intent
