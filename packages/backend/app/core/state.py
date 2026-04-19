"""Shared LangGraph state (story.md AgentState)."""

from __future__ import annotations

from typing import Any, TypedDict


class AgentState(TypedDict):
    """Multi-agent orchestration state passed between graph nodes."""

    user_id: str
    role: str
    query: str
    intent: str
    documents: list[Any]
    tool_result: dict[str, Any]
    audit_log: list[str]
    final_response: str
