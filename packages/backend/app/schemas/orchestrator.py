from typing import Any

from pydantic import BaseModel, Field

from app.schemas.chat import LLMProviderEnum


class OrchestratorRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=32000)
    top_k: int = Field(
        default=5, ge=1, le=20, description="RAG top-k when routed to document."
    )
    provider: LLMProviderEnum | None = Field(
        default=None,
        description="LLM backend for RAG / general paths; omit for DEFAULT_LLM_PROVIDER.",
    )
    model: str | None = Field(default=None, description="Optional model id override.")


class OrchestratorResponse(BaseModel):
    final_response: str
    intent: str
    original_query: str = Field(
        default="",
        description="Full user message before decomposition.",
    )
    sub_queries: list[str] = Field(
        default_factory=list,
        description="Atomic sub-queries after decomposition.",
    )
    task_results: list[dict[str, Any]] = Field(
        default_factory=list,
        description="Per sub-query: subquery, intent, answer, documents, tool_result.",
    )
    audit_log: list[str]
    documents: list[dict[str, Any]] = Field(
        default_factory=list,
        description="RAG source snippets (merged across document sub-tasks).",
    )
    tool_result: dict[str, Any] = Field(default_factory=dict)
