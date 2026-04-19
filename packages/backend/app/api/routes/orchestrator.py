"""Multi-agent orchestrator (LangGraph)."""

import logging

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.middleware.auth import get_current_user, verify_dev_token
from app.core.graph import run_orchestrator
from app.models.rbac import User
from app.schemas.orchestrator import OrchestratorRequest, OrchestratorResponse
from app.services.db import get_db

logger = logging.getLogger(__name__)

router = APIRouter(tags=["orchestrator"])


@router.post("/orchestrator/run", response_model=OrchestratorResponse)
def post_orchestrator_run(
    body: OrchestratorRequest,
    db: Session = Depends(get_db),
    _: None = Depends(verify_dev_token),
    user: User = Depends(get_current_user),
) -> OrchestratorResponse:
    """RBAC → decompose → router loop → agents (DB-audited) → aggregate."""
    state, trace_id, agent_run_id = run_orchestrator(
        db,
        user=user,
        query=body.query,
        provider=body.provider,
        model=body.model,
        top_k=body.top_k,
    )
    tool_result = dict(state.get("tool_result") or {})
    task_results = list(state.get("task_results") or [])
    if not task_results and tool_result.get("task_results"):
        task_results = list(tool_result["task_results"])
    logger.info(
        "orchestrator done user=%s trace=%s run=%s intent=%s sub_tasks=%s",
        user.id,
        trace_id,
        agent_run_id,
        state.get("intent"),
        len(state.get("sub_queries") or []),
    )
    return OrchestratorResponse(
        trace_id=trace_id,
        agent_run_id=agent_run_id,
        final_response=state.get("final_response") or "",
        intent=state.get("intent") or "",
        original_query=state.get("original_query") or body.query,
        sub_queries=list(state.get("sub_queries") or []),
        task_results=task_results,
        audit_log=list(state.get("audit_log") or []),
        documents=list(state.get("documents") or []),
        tool_result=tool_result,
    )
