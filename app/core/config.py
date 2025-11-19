from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration loaded from environment variables."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="allow")

    app_env: str = "dev"
    api_prefix: str = "/api/v1"
    log_level: str = "INFO"
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    external_base_url: str | None = None

    anthropic_api_key: str | None = None
    tavily_api_key: str | None = None
    openai_api_key: str | None = None
    weaviate_url: str = "http://localhost:8080"
    weaviate_grpc_port: int | None = None
    weaviate_api_key: str | None = None
    weaviate_collection_name: str = "Documents"
    allow_weaviate_fallback: bool = True

    langchain_api_key: str | None = None
    langchain_tracing_v2: bool = False

@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return cached application settings."""

    return Settings()
