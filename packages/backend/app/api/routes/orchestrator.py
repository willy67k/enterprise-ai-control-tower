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
    """Run router → document (RAG) | finance (demo) | general (direct LLM)."""
    state = run_orchestrator(
        db,
        user=user,
        query=body.query,
        provider=body.provider,
        model=body.model,
        top_k=body.top_k,
    )
    logger.info(
        "orchestrator done user=%s intent=%s audit_steps=%s",
        user.id,
        state.get("intent"),
        len(state.get("audit_log") or []),
    )
    return OrchestratorResponse(
        final_response=state.get("final_response") or "",
        intent=state.get("intent") or "",
        audit_log=list(state.get("audit_log") or []),
        documents=list(state.get("documents") or []),
        tool_result=dict(state.get("tool_result") or {}),
    )
