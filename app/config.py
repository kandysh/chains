"""Configuration management for the application."""

from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings."""

    app_name: str = "Chains API"
    app_version: str = "0.1.0"
    debug: bool = False

    # OpenAI
    openai_api_key: str = ""

    # Server
    host: str = "0.0.0.0"
    port: int = 8000

    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
