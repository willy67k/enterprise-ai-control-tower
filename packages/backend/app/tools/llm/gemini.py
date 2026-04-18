"""Google Gemini chat via LangChain."""

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_google_genai import ChatGoogleGenerativeAI

from app.config import Settings
from app.tools.llm.base import BaseProvider


class GeminiProvider(BaseProvider):
    def _api_key(self, settings: Settings) -> str:
        return settings.google_api_key

    def _missing_key_message(self) -> str:
        return "GOOGLE_API_KEY (or GEMINI_API_KEY) is not set; add it to .env"

    def _default_model(self, settings: Settings) -> str:
        return settings.gemini_model

    def _build_llm(self, *, api_key: str, model_name: str) -> BaseChatModel:
        return ChatGoogleGenerativeAI(
            model=model_name,
            api_key=api_key,
            temperature=self.temperature,
        )


_provider = GeminiProvider()


def chat_with_gemini(prompt: str, *, model: str | None = None) -> tuple[str, str]:
    """Send a single user message; return (assistant_text, model_used)."""
    return _provider.chat(prompt, model=model)
