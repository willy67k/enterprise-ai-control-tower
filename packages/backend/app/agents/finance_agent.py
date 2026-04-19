"""Finance path: deterministic demo metrics (no external market data)."""

from __future__ import annotations

import json
import logging

from app.core.state import AgentState

logger = logging.getLogger(__name__)


def _demo_payload() -> dict:
    return {
        "revenue_growth": "12%",
        "risk_score": 0.72,
        "insights": [
            "Revenue softness in Q2 aligns with elevated churn in the demo cohort.",
            "APAC volatility is above the rolling 4-quarter average (illustrative).",
        ],
        "_note": "synthetic_finance_agent_output",
    }


def finance_node(state: AgentState) -> dict:
    payload = _demo_payload()
    audit = state["audit_log"] + ["finance_agent: synthetic_kpis"]
    summary = (
        "Finance agent (demo): "
        f"revenue growth {payload['revenue_growth']}, "
        f"risk score {payload['risk_score']}. "
        f"Insights: {payload['insights'][0]}"
    )
    logger.debug("finance_node for user_id=%s", state["user_id"])
    return {
        "final_response": summary,
        "tool_result": {"finance": payload, "raw_json": json.dumps(payload)},
        "audit_log": audit,
    }
