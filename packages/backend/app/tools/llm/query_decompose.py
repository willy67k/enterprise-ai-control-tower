"""Split compound user messages into atomic sub-queries (OpenAI structured output)."""

from __future__ import annotations

import logging
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field

from app.config import get_settings
from app.tools.llm.errors import LLMConfigurationError

logger = logging.getLogger(__name__)

DECOMPOSE_MODEL = "gpt-4o-mini"


class DecomposedSubQueries(BaseModel):
    """Structured JSON: standalone sub-questions for multi-intent routing."""

    sub_queries: list[str] = Field(
        ...,
        min_length=1,
        max_length=8,
        description=(
            "Atomic sub-questions derived from the user message. Each item must stand "
            "alone (no pronouns like 'it' without referent). One item if there is a "
            "single clear request."
        ),
    )


_DECOMPOSE_SYSTEM = """You split user messages into separate sub-questions only when the user clearly asks for multiple distinct things in one turn.

Examples of when to split:
- Asking about personal/resume content AND company financials in the same message.
- Asking to summarize a policy AND to compute KPIs.

When to keep a single sub-query:
- One topic with follow-up detail.
- Ambiguous but unified request (do not over-split).

Each sub-query must be self-contained and readable without the rest of the message (replace pronouns with concrete nouns when needed).

Output 1–8 items. If there is only one intent, return exactly one string in sub_queries."""


def decompose_queries_structured_openai(message: str, *, role: str) -> list[str]:
    """Return atomic sub-queries via GPT-4o-mini + JSON schema."""
    settings = get_settings()
    key = (settings.openai_api_key or "").strip()
    if not key:
        raise LLMConfigurationError(
            "OPENAI_API_KEY is not set; query decomposition requires OpenAI",
        )

    llm = ChatOpenAI(
        api_key=key,
        model=DECOMPOSE_MODEL,
        temperature=0,
    )
    structured = llm.with_structured_output(
        DecomposedSubQueries,
        method="json_schema",
        strict=True,
    )
    messages = [
        SystemMessage(content=_DECOMPOSE_SYSTEM),
        HumanMessage(content=f"user_role: {role}\n\nuser_message:\n{message}"),
    ]
    out: DecomposedSubQueries = structured.invoke(messages)
    subs = [s.strip() for s in out.sub_queries if isinstance(s, str) and s.strip()]
    logger.debug("decompose: %s sub_queries", len(subs))
    return subs
