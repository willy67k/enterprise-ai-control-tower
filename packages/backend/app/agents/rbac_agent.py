"""RBAC gate: attach tool permissions from role (story.md permission matrix)."""

from __future__ import annotations

import logging

from app.core.state import AgentState

logger = logging.getLogger(__name__)

# role name (lowercase) -> permission keys used by the orchestrator
_ROLE_PERMISSIONS: dict[str, list[str]] = {
    "admin": ["rag", "finance", "system"],
    "finance_user": ["rag", "finance"],
    "analyst": ["rag"],
    "viewer": ["rag"],
}


def _normalize(name: str) -> str:
    return (name or "").strip().lower().replace(" ", "_")


def permissions_for_role(role: str) -> list[str]:
    key = _normalize(role)
    perms = _ROLE_PERMISSIONS.get(key)
    if perms is None:
        logger.debug("Unknown role %r — defaulting to viewer permissions", role)
        return list(_ROLE_PERMISSIONS["viewer"])
    return list(perms)


def permissions_for_roles(names: list[str]) -> list[str]:
    """Union of permissions across all roles (unknown role → viewer)."""
    acc: set[str] = set()
    for raw in names or ["viewer"]:
        acc.update(permissions_for_role(raw))
    return sorted(acc)


def rbac_gate_node(state: AgentState) -> dict:
    """Set ``permissions`` from ``role_names`` (union); log for in-graph audit trail."""
    names = list(state.get("role_names") or []) or [state["role"]]
    perms = permissions_for_roles(names)
    audit = state["audit_log"] + [
        f"rbac_gate: roles={','.join(names)} permissions={','.join(perms)}",
    ]
    return {"permissions": perms, "audit_log": audit}
