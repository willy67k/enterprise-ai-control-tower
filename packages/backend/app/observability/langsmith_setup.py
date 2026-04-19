"""Apply LangSmith / LangChain tracing env vars before LangGraph loads.

LangChain reads ``LANGCHAIN_TRACING_V2``, ``LANGCHAIN_API_KEY``, and
``LANGCHAIN_PROJECT`` from the process environment. This module syncs them
from :class:`~app.config.Settings` so a single ``.env`` drives the app.
"""

from __future__ import annotations

import logging
import os

from app.config import Settings

logger = logging.getLogger(__name__)


def apply_langsmith_from_settings(settings: Settings) -> bool:
    """If an API key is configured, export LangSmith-related env vars.

    Returns whether tracing was activated (key present and tracing flag on).
    """
    key = (settings.langchain_api_key or "").strip()

    if not key:
        return False

    os.environ["LANGCHAIN_API_KEY"] = key

    if settings.langchain_tracing_v2:
        os.environ["LANGCHAIN_TRACING_V2"] = "true"
    else:
        os.environ["LANGCHAIN_TRACING_V2"] = "false"

    project = (settings.langchain_project or "").strip()
    if project:
        os.environ["LANGCHAIN_PROJECT"] = project

    endpoint = (settings.langchain_endpoint or "").strip()
    if endpoint:
        os.environ["LANGCHAIN_ENDPOINT"] = endpoint

    logger.info(
        "LangSmith: LANGCHAIN_TRACING_V2=%s project=%s",
        os.environ.get("LANGCHAIN_TRACING_V2"),
        project or "(default)",
    )
    return bool(settings.langchain_tracing_v2)
