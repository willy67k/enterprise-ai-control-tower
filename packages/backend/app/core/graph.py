"""LangGraph: decompose → router loop → document | finance | general → aggregate."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Literal

from langgraph.graph import END, START, StateGraph

from app.agents.decompose_agent import decompose_node
from app.agents.document_agent import document_node
from app.agents.finance_agent import finance_node
from app.agents.general_agent import general_node
from app.agents.multi_task_nodes import aggregate_node, task_checkpoint_node
from app.agents.router_agent import router_node
from app.core.state import AgentState

if TYPE_CHECKING:
    from sqlalchemy.orm import Session

    from app.models.rbac import User

logger = logging.getLogger(__name__)

_compiled_orchestrator = None


def _primary_role_name(user: User) -> str:
    roles = getattr(user, "roles", None) or []
    if not roles:
        return "viewer"
    return roles[0].name


def _route_after_router(state: AgentState) -> Literal["document", "finance", "general"]:
    intent = state.get("intent") or "general"
    if intent == "document":
        return "document"
    if intent == "finance":
        return "finance"
    return "general"


def _route_after_checkpoint(state: AgentState) -> Literal["router", "aggregate"]:
    sub_queries = state.get("sub_queries") or []
    task_idx = int(state.get("task_idx") or 0)
    if task_idx < len(sub_queries):
        return "router"
    return "aggregate"


def build_orchestrator_graph() -> StateGraph:
    g = StateGraph(AgentState)
    g.add_node("decompose", decompose_node)
    g.add_node("router", router_node)
    g.add_node("document", document_node)
    g.add_node("finance", finance_node)
    g.add_node("general", general_node)
    g.add_node("task_checkpoint", task_checkpoint_node)
    g.add_node("aggregate", aggregate_node)

    g.add_edge(START, "decompose")
    g.add_edge("decompose", "router")
    g.add_conditional_edges("router", _route_after_router)
    g.add_edge("document", "task_checkpoint")
    g.add_edge("finance", "task_checkpoint")
    g.add_edge("general", "task_checkpoint")
    g.add_conditional_edges("task_checkpoint", _route_after_checkpoint)
    g.add_edge("aggregate", END)
    return g


def get_compiled_orchestrator():
    global _compiled_orchestrator
    if _compiled_orchestrator is None:
        _compiled_orchestrator = build_orchestrator_graph().compile()
        logger.info("Compiled LangGraph orchestrator")
    return _compiled_orchestrator


def run_orchestrator(
    db: Session,
    *,
    user: User,
    query: str,
    provider: str | None,
    model: str | None,
    top_k: int,
) -> AgentState:
    graph = get_compiled_orchestrator()
    initial: AgentState = {
        "user_id": str(user.id),
        "role": _primary_role_name(user),
        "original_query": query,
        "query": query,
        "sub_queries": [],
        "task_idx": 0,
        "task_results": [],
        "intent": "",
        "documents": [],
        "tool_result": {},
        "audit_log": [],
        "final_response": "",
    }
    config = {
        "configurable": {
            "db": db,
            "owner_id": str(user.id),
            "llm_provider": provider,
            "llm_model": model,
            "rag_top_k": top_k,
        }
    }
    result = graph.invoke(initial, config=config)
    return result  # type: ignore[return-value]
