"""Multi-intent loop: checkpoint after each agent, then aggregate all answers."""

from __future__ import annotations

import logging

from app.core.state import AgentState

logger = logging.getLogger(__name__)


def task_checkpoint_node(state: AgentState) -> dict:
    """Append current sub-task outcome; advance query or mark batch complete."""
    sub_queries = list(state.get("sub_queries") or [])
    idx = int(state.get("task_idx") or 0)
    tr_entry = {
        "subquery": state.get("query") or "",
        "intent": state.get("intent") or "",
        "answer": state.get("final_response") or "",
        "tool_result": dict(state.get("tool_result") or {}),
        "documents": list(state.get("documents") or []),
    }
    results = list(state.get("task_results") or []) + [tr_entry]
    next_i = idx + 1
    log = list(state.get("audit_log") or []) + [
        f"task_checkpoint: part {idx + 1}/{len(sub_queries)} intent={tr_entry['intent']}"
    ]

    if next_i < len(sub_queries):
        return {
            "task_results": results,
            "task_idx": next_i,
            "query": sub_queries[next_i],
            "intent": "",
            "final_response": "",
            "documents": [],
            "tool_result": {},
            "audit_log": log,
        }

    return {
        "task_results": results,
        "task_idx": next_i,
        "audit_log": log,
    }


def aggregate_node(state: AgentState) -> dict:
    """Merge per-task answers into one final_response and combined tool_result."""
    task_results = list(state.get("task_results") or [])
    sub_queries = list(state.get("sub_queries") or [])
    parts: list[str] = []
    for i, tr in enumerate(task_results, start=1):
        intent = tr.get("intent") or "unknown"
        sq = tr.get("subquery") or ""
        ans = tr.get("answer") or ""
        parts.append(f"**Part {i}** ({intent})\n\n*{sq}*\n\n{ans}")

    body = "\n\n---\n\n".join(parts) if parts else (state.get("final_response") or "")

    all_docs: list = []
    for tr in task_results:
        all_docs.extend(tr.get("documents") or [])

    intents = [str(tr.get("intent") or "") for tr in task_results if tr.get("intent")]
    intent_field = ",".join(intents) if intents else "general"

    log = list(state.get("audit_log") or []) + ["aggregate: merged multi-part reply"]
    logger.debug("aggregate: %s parts intent=%s", len(task_results), intent_field)

    return {
        "final_response": body,
        "documents": all_docs,
        "intent": intent_field,
        "tool_result": {
            "multi_task": True,
            "sub_queries": sub_queries,
            "task_results": task_results,
        },
        "audit_log": log,
    }
