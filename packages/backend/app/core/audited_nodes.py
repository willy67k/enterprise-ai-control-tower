"""Wrap LangGraph nodes to record each step to agent_steps + audit_logs."""

from __future__ import annotations

import inspect
import logging
import time
import uuid
from collections.abc import Callable
from typing import Any, Optional

from langchain_core.runnables import RunnableConfig
from sqlalchemy.orm import Session

from app.core.state import AgentState
from app.services.agent_audit_service import record_graph_node

logger = logging.getLogger(__name__)


def _snapshot_input(state: AgentState, step_name: str) -> dict[str, Any]:
    return {
        "step": step_name,
        "user_id": state.get("user_id"),
        "role": state.get("role"),
        "role_names": state.get("role_names"),
        "permissions": state.get("permissions"),
        "original_query": (state.get("original_query") or "")[:8_000],
        "query": (state.get("query") or "")[:8_000],
        "task_idx": state.get("task_idx"),
        "intent": state.get("intent"),
        "sub_queries_len": len(state.get("sub_queries") or []),
    }


def wrap_audited(
    step_name: str, fn: Callable[..., dict[str, Any]]
) -> Callable[..., dict[str, Any]]:
    """Invoke ``fn`` and persist input/output/latency when run metadata is in config."""

    sig = inspect.signature(fn)
    param_names = list(sig.parameters.keys())
    fn_wants_config = len(param_names) >= 2 and param_names[1] == "config"

    # LangGraph only injects ``config`` if the wrapper exposes a typed ``config``
    # parameter; ``RunnableConfig | None`` is not accepted—use ``Optional[...]`` or
    # leave unannotated (see KWARGS_CONFIG_KEYS in langgraph._internal._runnable).
    def wrapped(
        state: AgentState,
        config: Optional[RunnableConfig] = None,
    ) -> dict[str, Any]:
        cfg = (config.get("configurable") or {}) if config else {}
        db: Session | None = cfg.get("db")
        run_id_raw = cfg.get("agent_run_id")
        trace_id = cfg.get("trace_id")

        t0 = time.perf_counter()
        err: BaseException | None = None
        out: dict[str, Any] | None = None
        try:
            if fn_wants_config:
                out = fn(state, config)
            else:
                out = fn(state)
        except BaseException as e:
            err = e
            raise
        finally:
            elapsed_ms = int((time.perf_counter() - t0) * 1000)
            if db is None or not run_id_raw or not trace_id:
                if db is None:
                    logger.debug(
                        "audited_nodes: skip persist (no db) step=%s", step_name
                    )
            else:
                try:
                    run_id = uuid.UUID(str(run_id_raw))
                    user_id = uuid.UUID(str(state.get("user_id")))
                    payload_in = _snapshot_input(state, step_name)
                    if err is not None:
                        payload_out: dict[str, Any] = {
                            "error": str(err),
                            "error_type": type(err).__name__,
                        }
                    elif out is not None:
                        payload_out = dict(out)
                    else:
                        payload_out = {}
                    record_graph_node(
                        db,
                        run_id=run_id,
                        user_id=user_id,
                        trace_id=str(trace_id),
                        step_name=step_name,
                        input_payload=payload_in,
                        output_payload=payload_out,
                        latency_ms=elapsed_ms,
                    )
                except Exception:
                    logger.exception(
                        "audited_nodes: failed to persist step=%s run_id=%s",
                        step_name,
                        run_id_raw,
                    )

        return out  # type: ignore[return-value]

    return wrapped
