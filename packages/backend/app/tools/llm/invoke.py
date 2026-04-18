"""Dispatch chat to OpenAI, Gemini, or Anthropic."""

from typing import Literal

from app.config import get_settings
from app.tools.llm.claude import chat_with_claude
from app.tools.llm.errors import LLMConfigurationError
from app.tools.llm.gemini import chat_with_gemini
from app.tools.llm.openai import chat_with_openai

LLMProvider = Literal["openai", "gemini", "anthropic"]


def normalize_provider(name: str | None) -> LLMProvider:
    settings = get_settings()
    raw = (name or settings.default_llm_provider or "openai").strip().lower()
    if raw not in ("openai", "gemini", "anthropic"):
        raise LLMConfigurationError(
            f"Unknown provider {name!r}. Use openai, gemini, or anthropic.",
        )
    return raw  # type: ignore[return-value]


def chat(
    prompt: str,
    *,
    provider: str | None,
    model: str | None,
) -> tuple[str, str, LLMProvider]:
    """Return (reply, model_used, provider_used)."""
    p = normalize_provider(provider)
    if p == "openai":
        reply, m = chat_with_openai(prompt, model=model)
        return reply, m, "openai"
    if p == "gemini":
        reply, m = chat_with_gemini(prompt, model=model)
        return reply, m, "gemini"
    reply, m = chat_with_claude(prompt, model=model)
    return reply, m, "anthropic"
