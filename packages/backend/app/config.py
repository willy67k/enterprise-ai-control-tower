from functools import lru_cache

from pydantic import AliasChoices, Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment and optional `.env` file."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "Enterprise AI Control Tower"
    app_version: str = "0.1.0"
    environment: str = "development"
    log_level: str = "INFO"

    # PostgreSQL (Docker: packages/backend/docker-compose.yml)
    database_url: str = (
        "postgresql+psycopg://postgres:postgres@localhost:5432/control_tower"
    )
    database_echo: bool = False

    # Phase 3 fake auth (replace in production)
    dev_api_token: str = "dev-insecure-change-me"

    # Phase 4 — LLM providers (set the API key for each provider you use)
    default_llm_provider: str = "openai"

    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"

    # Gemini accepts GOOGLE_API_KEY or GEMINI_API_KEY
    google_api_key: str = Field(
        default="",
        validation_alias=AliasChoices("GOOGLE_API_KEY", "GEMINI_API_KEY"),
    )
    gemini_model: str = "gemini-2.0-flash"

    anthropic_api_key: str = ""
    anthropic_model: str = "claude-3-5-haiku-20241022"

    # Phase 5 — uploads & RAG (OpenAI embeddings; VECTOR(1536) in Postgres)
    upload_dir: str = "data/uploads"
    max_upload_bytes: int = 10 * 1024 * 1024
    rag_chunk_size: int = 1000
    rag_chunk_overlap: int = 200
    openai_embedding_model: str = "text-embedding-3-small"

    @field_validator("default_llm_provider")
    @classmethod
    def default_llm_provider_ok(cls, v: str) -> str:
        allowed = frozenset({"openai", "gemini", "anthropic"})
        n = (v or "").strip().lower()
        if n not in allowed:
            raise ValueError(
                f"default_llm_provider must be one of: {', '.join(sorted(allowed))}"
            )
        return n


@lru_cache
def get_settings() -> Settings:
    return Settings()
