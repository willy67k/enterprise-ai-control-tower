from functools import lru_cache

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


@lru_cache
def get_settings() -> Settings:
    return Settings()
