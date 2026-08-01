from functools import lru_cache

from pydantic import AliasChoices, Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    APP_NAME: str = "AI English Teacher"
    APP_ENV: str = "development"
    DEBUG: bool = False

    DATABASE_URL: str = "sqlite+aiosqlite:///./ai_english_teacher.db"

    JWT_SECRET: str = Field(validation_alias=AliasChoices("JWT_SECRET", "JWT_SECRET_KEY"))
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    BUILD_COMMIT_SHA: str = ""
    BUILD_TIMESTAMP: str = ""

    SENTRY_DSN: str = ""

    XAI_API_KEY: str = ""
    GROK_MODEL: str = "grok-2-1212"
    GROK_BASE_URL: str = "https://api.x.ai/v1/chat/completions"

    OPENAI_API_KEY: str = ""
    WHISPER_MODEL: str = "whisper-1"
    WHISPER_BASE_URL: str = "https://api.openai.com/v1/audio/transcriptions"

    TTS_VOICE_FEMALE: str = "en-US-JennyNeural"
    TTS_VOICE_MALE: str = "en-US-GuyNeural"

    # RAG embeddings (sentence-transformers/all-MiniLM-L6-v2 default — Grok does not provide vectors)
    EMBEDDING_DIMENSION: int = 384

    # Knowledge ingestion chunking (characters; token-aware splitting is a future enhancement)
    INGESTION_CHUNK_SIZE: int = 1000
    INGESTION_CHUNK_OVERLAP: int = 200

    CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def normalize_database_url(cls, value: str) -> str:
        if not isinstance(value, str):
            return value
        if value.startswith("postgres://"):
            return value.replace("postgres://", "postgresql+asyncpg://", 1)
        if value.startswith("postgresql://"):
            return value.replace("postgresql://", "postgresql+asyncpg://", 1)
        return value

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, value: str | list[str]) -> list[str]:
        if isinstance(value, list):
            return value
        if isinstance(value, str):
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        return ["http://localhost:3000"]


@lru_cache
def get_settings() -> Settings:
    return Settings()  # type: ignore[call-arg]
