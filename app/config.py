from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    processor_port: int = 8001
    secret_key: str = Field(default="changeme", description="JWT signing secret")
    jwt_algorithm: str = "HS256"

    # Database (PostgreSQL)
    database_url: str = (
        "postgresql+asyncpg://postgres:postgres@localhost:5432/trade_recon"
    )

    # Redis
    redis_url: str = "redis://localhost:6379"

    # AWS / S3
    aws_access_key_id: str = ""
    aws_secret_access_key: str = ""
    aws_region: str = "us-east-1"
    s3_bucket: str = "trade-recon"
    s3_upload_prefix: str = "uploads"
    presigned_url_expiry: int = 900  # 15 minutes

    # LLM
    openai_api_key: str = ""
    llm_model: str = "gpt-4o"

    # Matching thresholds
    fuzzy_high_confidence: float = 0.90
    fuzzy_ambiguous_min: float = 0.70

    # Redis stream / consumer group names
    processing_stream: str = "processing:queue"
    consumer_group: str = "processor-group"
    consumer_name: str = "processor-1"
    stream_read_count: int = 1
    stream_block_ms: int = 5000  # 5s long-poll

    # Logging
    log_level: str = "INFO"


@lru_cache
def get_settings() -> Settings:
    return Settings()
