from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Central application configuration. All values are overridable via
    environment variables (or a .env file locally). Never hardcode secrets
    or connection strings elsewhere in the codebase — import `settings`.
    """

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # App
    ENVIRONMENT: str = "development"
    API_V1_PREFIX: str = "/api/v1"

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://practicepro:practicepro@db:5432/practicepro"
    DATABASE_URL_SYNC: str = "postgresql+psycopg2://practicepro:practicepro@db:5432/practicepro"

    # Redis / Celery
    REDIS_URL: str = "redis://redis:6379/0"
    CELERY_BROKER_URL: str = "redis://redis:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://redis:6379/1"

    # Storage
    STORAGE_BACKEND: str = "local"  # "local" | "s3"
    LOCAL_STORAGE_PATH: str = "/data/audio"
    S3_BUCKET: str | None = None
    S3_ENDPOINT_URL: str | None = None

    # Upload validation
    MAX_UPLOAD_SIZE_MB: int = 50
    ALLOWED_AUDIO_EXTENSIONS: set[str] = {".wav", ".mp3", ".m4a", ".flac", ".ogg"}

    # LLM
    ANTHROPIC_API_KEY: str | None = None
    FEEDBACK_MODEL: str = "claude-sonnet-4-6"

    # CORS
    CORS_ORIGINS: list[str] = ["http://localhost:5173", "http://localhost:3000"]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
