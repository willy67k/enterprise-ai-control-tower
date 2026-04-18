"""OpenAI chat via LangChain."""

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_openai import ChatOpenAI

from app.config import Settings
from app.tools.llm.base import BaseProvider


class OpenAIProvider(BaseProvider):
    def _api_key(self, settings: Settings) -> str:
        return settings.openai_api_key

    def _missing_key_message(self) -> str:
        return "OPENAI_API_KEY is not set; add it to .env"

    def _default_model(self, settings: Settings) -> str:
        return settings.openai_model

    def _build_llm(self, *, api_key: str, model_name: str) -> BaseChatModel:
        return ChatOpenAI(
            api_key=api_key,
            model=model_name,
            temperature=self.temperature,
        )


_provider = OpenAIProvider()


def chat_with_openai(prompt: str, *, model: str | None = None) -> tuple[str, str]:
    """Send a single user message; return (assistant_text, model_used)."""
    return _provider.chat(prompt, model=model)
