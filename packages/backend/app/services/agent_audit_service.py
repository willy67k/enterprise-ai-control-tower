"""Persist LangGraph runs, per-node steps, and audit rows to Postgres."""

from __future__ import annotations

import logging
import uuid
from datetime import datetime, timezone
from typing import Any

from sqlalchemy.orm import Session

from app.models.agent_audit import AgentRun, AgentStep, AuditLog

logger = logging.getLogger(__name__)

_MAX_IO_TEXT = 120_000
_MAX_JSON_DEPTH = 10
_MAX_DICT_KEYS = 120
_MAX_LIST_ITEMS = 80
_MAX_STR = 16_000


def json_safe(value: Any, *, depth: int = 0) -> Any:
    """Make a value JSON-serializable for JSONB; truncate large structures."""
    if depth > _MAX_JSON_DEPTH:
        return "<max_depth>"
    if value is None or isinstance(value, (bool, int, float)):
        return value
    if isinstance(value, str):
        if len(value) > _MAX_STR:
            return value[:_MAX_STR] + "…"
        return value
    if isinstance(value, uuid.UUID):
        return str(value)
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, bytes):
        return f"<bytes len={len(value)}>"
    if isinstance(value, dict):
        items = list(value.items())[:_MAX_DICT_KEYS]
        return {str(k): json_safe(v, depth=depth + 1) for k, v in items}
    if isinstance(value, (list, tuple)):
        return [json_safe(x, depth=depth + 1) for x in value[:_MAX_LIST_ITEMS]]
    return str(value)[:_MAX_STR]


def begin_agent_run(
    db: Session,
    *,
    user_id: uuid.UUID,
    trace_id: str,
    input_text: str,
) -> AgentRun:
    run = AgentRun(
        user_id=user_id,
        trace_id=trace_id,
        input=(input_text or "")[:_MAX_IO_TEXT],
        status="running",
    )
    db.add(run)
    db.commit()
    db.refresh(run)
    return run


def finish_agent_run(
    db: Session,
    run_id: uuid.UUID,
    *,
    status: str,
    output: str | None,
) -> None:
    run = db.get(AgentRun, run_id)
    if run is None:
        logger.warning("finish_agent_run: missing run_id=%s", run_id)
        return
    run.status = status
    run.output = (output or "")[:_MAX_IO_TEXT] if output is not None else None
    run.finished_at = datetime.now(timezone.utc)
    db.add(run)
    db.commit()


def record_graph_node(
    db: Session,
    *,
    run_id: uuid.UUID,
    user_id: uuid.UUID,
    trace_id: str,
    step_name: str,
    input_payload: dict[str, Any],
    output_payload: dict[str, Any],
    latency_ms: int,
) -> None:
    inp = json_safe(input_payload)
    out = json_safe(output_payload)
    if not isinstance(inp, dict):
        inp = {"_raw": inp}
    if not isinstance(out, dict):
        out = {"_raw": out}

    step = AgentStep(
        run_id=run_id,
        step_name=step_name,
        input=inp,
        output=out,
        latency_ms=latency_ms,
    )
    db.add(step)
    log = AuditLog(
        trace_id=trace_id,
        user_id=user_id,
        agent=step_name,
        event_type="graph_node",
        payload={"input": inp, "output": out, "latency_ms": latency_ms},
    )
    db.add(log)
    db.commit()
