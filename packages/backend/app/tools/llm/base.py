"""Shared chat flow for LangChain-backed LLM providers."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import HumanMessage

from app.config import Settings, get_settings
from app.tools.llm.errors import LLMConfigurationError


def message_content_to_str(message: Any) -> str:
    """Normalize AIMessage (or similar) content to a plain string."""
    content = getattr(message, "content", None)
    if not isinstance(content, str):
        content = str(content)
    return content


class BaseProvider(ABC):
    """One-shot chat: validate API key, build model, invoke, return text + model id."""

    temperature: float = 0.7

    @abstractmethod
    def _api_key(self, settings: Settings) -> str:
        """Raw API key string from settings (may be empty)."""

    @abstractmethod
    def _missing_key_message(self) -> str:
        """Raised as LLMConfigurationError when key is missing."""

    @abstractmethod
    def _default_model(self, settings: Settings) -> str:
        """Fallback model id when request does not override."""

    @abstractmethod
    def _build_llm(self, *, api_key: str, model_name: str) -> BaseChatModel:
        """Construct the LangChain chat model for this vendor."""

    def chat(self, prompt: str, *, model: str | None = None) -> tuple[str, str]:
        settings = get_settings()
        key = (self._api_key(settings) or "").strip()
        if not key:
            raise LLMConfigurationError(self._missing_key_message())
        model_name = (model or self._default_model(settings)).strip()
        llm = self._build_llm(api_key=key, model_name=model_name)
        out = llm.invoke([HumanMessage(content=prompt)])
        return message_content_to_str(out), model_name
