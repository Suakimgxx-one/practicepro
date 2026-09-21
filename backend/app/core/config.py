from functools import lru_cache

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    ENVIRONMENT: str = "development"
    API_V1_PREFIX: str = "/api/v1"

    DATABASE_URL: str = "postgresql+asyncpg://practicepro:practicepro@db:5432/practicepro"
    DATABASE_URL_SYNC: str = "postgresql+psycopg2://practicepro:practicepro@db:5432/practicepro"

    REDIS_URL: str = "redis://redis:6379/0"
    CELERY_BROKER_URL: str = "redis://redis:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://redis:6379/1"

    STORAGE_BACKEND: str = "local"
    LOCAL_STORAGE_PATH: str = "/data/audio"
    S3_BUCKET: str | None = None
    S3_ENDPOINT_URL: str | None = None

    MAX_UPLOAD_SIZE_MB: int = 50
    ALLOWED_AUDIO_EXTENSIONS: set[str] = {".wav", ".mp3", ".m4a", ".flac", ".ogg"}

    ANTHROPIC_API_KEY: str | None = None
    FEEDBACK_MODEL: str = "claude-sonnet-4-6"

    CORS_ORIGINS: list[str] = ["http://localhost:5173", "http://localhost:3000"]

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def _ensure_async_driver(cls, v: str) -> str:
        # Most hosting platforms (Railway, Render, Heroku, Fly.io) hand
        # you a single plain "postgresql://" connection string via a
        # DATABASE_URL env var — that's the near-universal convention.
        # SQLAlchemy's async engine needs the +asyncpg driver suffix
        # explicit, though, so we insert it here if it's missing. This
        # means deploying anywhere just requires setting DATABASE_URL
        # to whatever the host gives you, verbatim — no manual string
        # surgery, and no dependency on that host's internal variable
        # naming for individual connection parts (user/password/host).
        if isinstance(v, str) and v.startswith("postgresql://"):
            return v.replace("postgresql://", "postgresql+asyncpg://", 1)
        return v

    @field_validator("DATABASE_URL_SYNC", mode="before")
    @classmethod
    def _ensure_sync_driver(cls, v: str) -> str:
        # Same idea as above, but for the sync engine Celery workers
        # use (see app/db/session.py) — +psycopg2 instead of +asyncpg.
        # In practice this means DATABASE_URL and DATABASE_URL_SYNC can
        # both be set to the exact same host-provided connection
        # string; each gets the correct driver inserted independently.
        if isinstance(v, str) and v.startswith("postgresql://"):
            return v.replace("postgresql://", "postgresql+psycopg2://", 1)
        return v


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
