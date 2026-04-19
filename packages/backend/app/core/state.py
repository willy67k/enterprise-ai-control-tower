"""Shared LangGraph state (story.md AgentState + multi-intent fields)."""

from __future__ import annotations

from typing import Any, TypedDict


class AgentState(TypedDict):
    """Multi-agent orchestration state passed between graph nodes."""

    user_id: str
    #: Primary role label (first assigned role; used for intent hints).
    role: str
    #: All role names from the DB (union drives RBAC permissions).
    role_names: list[str]
    #: Effective permissions for this run (``rag``, ``finance``, ``system``).
    permissions: list[str]
    #: Full user message (set once at graph entry).
    original_query: str
    #: Current atomic sub-query (router + leaf agents use this).
    query: str
    #: After decompose: all sub-queries; router loops by task_idx.
    sub_queries: list[str]
    task_idx: int
    task_results: list[dict[str, Any]]
    intent: str
    documents: list[Any]
    tool_result: dict[str, Any]
    audit_log: list[str]
    final_response: str
