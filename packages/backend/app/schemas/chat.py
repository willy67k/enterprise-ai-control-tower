from typing import Literal

from pydantic import BaseModel, Field

LLMProviderEnum = Literal["openai", "gemini", "anthropic"]


class ChatRequest(BaseModel):
    prompt: str = Field(..., min_length=1, max_length=32000)
    provider: LLMProviderEnum | None = Field(
        default=None,
        description="LLM backend; omit to use DEFAULT_LLM_PROVIDER from settings.",
    )
    model: str | None = Field(
        default=None,
        description="Optional model id; defaults per provider in settings.",
    )


class ChatResponse(BaseModel):
    reply: str
    model: str
    provider: LLMProviderEnum
