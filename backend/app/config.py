from functools import lru_cache

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    api_host: str = Field(default="0.0.0.0", alias="API_HOST")
    api_port: int = Field(default=8000, alias="API_PORT")
    debug: bool = Field(default=True, alias="DEBUG")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")

    database_url: str = Field(..., alias="DATABASE_URL")
    sync_database_url: str = Field(..., alias="SYNC_DATABASE_URL")
    redis_url: str = Field(..., alias="REDIS_URL")

    celery_broker_url: str = Field(..., alias="CELERY_BROKER_URL")
    celery_result_backend: str = Field(..., alias="CELERY_RESULT_BACKEND")
    celery_task_timeout: int = Field(default=3600, alias="CELERY_TASK_TIMEOUT")
    celery_max_retries: int = Field(default=3, alias="CELERY_MAX_RETRIES")

    secret_key: str = Field(..., alias="SECRET_KEY")
    access_token_expire_minutes: int = Field(default=60, alias="ACCESS_TOKEN_EXPIRE_MINUTES")
    refresh_token_expire_days: int = Field(default=14, alias="REFRESH_TOKEN_EXPIRE_DAYS")

    github_client_id: str = Field(default="", alias="GITHUB_CLIENT_ID")
    github_client_secret: str = Field(default="", alias="GITHUB_CLIENT_SECRET")
    github_redirect_uri: str = Field(default="", alias="GITHUB_REDIRECT_URI")
    github_api_rate_limit: int = Field(default=5000, alias="GITHUB_API_RATE_LIMIT")

    groq_api_key: str = Field(default="", alias="GROQ_API_KEY")
    groq_model: str = Field(default="llama-3.1-70b-versatile", alias="GROQ_MODEL")
    openai_api_key: str = Field(default="", alias="OPENAI_API_KEY")
    openai_model: str = Field(default="gpt-3.5-turbo", alias="OPENAI_MODEL")

    rate_limit_per_minute: int = Field(default=60, alias="RATE_LIMIT_PER_MINUTE")

    cache_ttl_seconds: int = Field(default=300, alias="CACHE_TTL_SECONDS")
    db_cache_ttl_hours: int = Field(default=24, alias="DB_CACHE_TTL_HOURS")
    redis_cache_prefix: str = Field(default="devforge:cache:", alias="REDIS_CACHE_PREFIX")

    cors_origins: list[str] = Field(default_factory=lambda: ["http://localhost:3000"], alias="CORS_ORIGINS")

    enable_metrics: bool = Field(default=True, alias="ENABLE_METRICS")

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_origins(cls, value: str | list[str]) -> list[str]:
        if isinstance(value, list):
            return value
        if isinstance(value, str):
            return [item.strip() for item in value.split(",") if item.strip()]
        return ["http://localhost:3000"]


@lru_cache
def get_settings() -> Settings:
    return Settings()
