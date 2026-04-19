"""LangGraph: RBAC → decompose → router loop → agents → aggregate (audited)."""

from __future__ import annotations

import logging
import uuid
from typing import TYPE_CHECKING, Any, Literal

from langgraph.graph import END, START, StateGraph

from app.agents.decompose_agent import decompose_node
from app.agents.document_agent import document_node
from app.agents.finance_agent import finance_node
from app.agents.general_agent import general_node
from app.agents.multi_task_nodes import aggregate_node, task_checkpoint_node
from app.agents.rbac_agent import rbac_gate_node
from app.agents.router_agent import router_node
from app.core.audited_nodes import wrap_audited
from app.core.state import AgentState
from app.services.agent_audit_service import begin_agent_run, finish_agent_run

if TYPE_CHECKING:
    from sqlalchemy.orm import Session

    from app.models.rbac import User

logger = logging.getLogger(__name__)

_compiled_orchestrator = None


def _role_names(user: User) -> list[str]:
    roles = getattr(user, "roles", None) or []
    if not roles:
        return ["viewer"]
    return [r.name for r in roles]


def _primary_role_name(user: User) -> str:
    return _role_names(user)[0]


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
    g.add_node("rbac_gate", wrap_audited("rbac_gate", rbac_gate_node))
    g.add_node("decompose", wrap_audited("decompose", decompose_node))
    g.add_node("router", wrap_audited("router", router_node))
    g.add_node("document", wrap_audited("document", document_node))
    g.add_node("finance", wrap_audited("finance", finance_node))
    g.add_node("general", wrap_audited("general", general_node))
    g.add_node("task_checkpoint", wrap_audited("task_checkpoint", task_checkpoint_node))
    g.add_node("aggregate", wrap_audited("aggregate", aggregate_node))

    g.add_edge(START, "rbac_gate")
    g.add_edge("rbac_gate", "decompose")
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
) -> tuple[dict[str, Any], str, str]:
    """Return ``(final_state_dict, trace_id, agent_run_id)``."""
    graph = get_compiled_orchestrator()
    trace_id = str(uuid.uuid4())
    run = begin_agent_run(
        db,
        user_id=user.id,
        trace_id=trace_id,
        input_text=query,
    )
    run_id = run.id

    initial: AgentState = {
        "user_id": str(user.id),
        "role": _primary_role_name(user),
        "role_names": _role_names(user),
        "permissions": [],
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
        "run_name": f"orchestrator-{trace_id[:8]}",
        "tags": ["orchestrator", "multi-agent", "control-tower"],
        "metadata": {
            "trace_id": trace_id,
            "agent_run_id": str(run_id),
            "user_id": str(user.id),
            "llm_provider": provider or "",
            "llm_model": model or "",
        },
        "configurable": {
            "db": db,
            "owner_id": str(user.id),
            "llm_provider": provider,
            "llm_model": model,
            "rag_top_k": top_k,
            "trace_id": trace_id,
            "agent_run_id": str(run_id),
        },
    }
    try:
        raw = graph.invoke(initial, config=config)
        result: dict[str, Any] = dict(raw)
        finish_agent_run(
            db,
            run_id,
            status="success",
            output=result.get("final_response"),
        )
    except BaseException:
        finish_agent_run(db, run_id, status="failed", output=None)
        raise

    return result, trace_id, str(run_id)
