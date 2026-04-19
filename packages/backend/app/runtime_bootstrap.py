"""Side effects on import: LangSmith env before any LangChain/LangGraph import."""

from __future__ import annotations

from app.config import get_settings
from app.observability.langsmith_setup import apply_langsmith_from_settings

apply_langsmith_from_settings(get_settings())
