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

    # Redis Configuration
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    redis_password: str = None

    # Storage Configuration
    storage_type: str = "local"  # 'local' or 's3'
    storage_path: str = "storage"  # For local storage
    s3_bucket_name: str = "confirmations"
    s3_endpoint_url: str = None
    aws_access_key_id: str = None
    aws_secret_access_key: str = None
    aws_region: str = "us-east-1"

    # Job Configuration
    job_timeout: str = "10h"
    max_retries: int = 3

    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
