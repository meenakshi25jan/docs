import json
from functools import lru_cache
from typing import Any

from pydantic import field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "AI English Teacher"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    API_V1_PREFIX: str = "/api/v1"

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/ai_english_teacher"
    DATABASE_POOL_SIZE: int = 20
    DATABASE_MAX_OVERFLOW: int = 10

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # JWT
    JWT_SECRET_KEY: str = "change-me-in-production-use-rs256-key-pair"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 hours (was 15 min — caused "Invalid token" too quickly)
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # OAuth2
    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""
    MICROSOFT_CLIENT_ID: str = ""
    MICROSOFT_CLIENT_SECRET: str = ""
    OAUTH_REDIRECT_BASE_URL: str = "http://localhost:8000"

    # Azure OpenAI — powers Microsoft Copilot in custom apps
    AZURE_OPENAI_ENDPOINT: str = ""
    AZURE_OPENAI_API_KEY: str = ""
    AZURE_OPENAI_DEPLOYMENT: str = "gpt-4o-mini"
    AZURE_OPENAI_API_VERSION: str = "2024-12-01-preview"

    # OpenAI / Groq (OpenAI-compatible APIs)
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4o"
    OPENAI_BASE_URL: str = ""  # e.g. https://api.groq.com/openai/v1

    # LLM provider: auto | copilot | azure | openai | ollama | mock
    AI_PROVIDER: str = "auto"
    OLLAMA_BASE_URL: str = ""
    OLLAMA_MODEL: str = "llama3.2"

    # Azure Speech
    AZURE_SPEECH_KEY: str = ""
    AZURE_SPEECH_REGION: str = "eastus"

    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 100
    RATE_LIMIT_TENANT_PER_MINUTE: int = 1000

    # CORS (comma-separated or JSON array)
    CORS_ORIGINS: list[str] = [
        "http://localhost:3000",
        "https://ai-english-teacher-web.onrender.com",
    ]

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v: Any) -> list[str]:
        if isinstance(v, list):
            origins = v
        elif isinstance(v, str):
            v = v.strip()
            if not v:
                origins = ["http://localhost:3000"]
            elif v.startswith("["):
                origins = json.loads(v)
            else:
                origins = [origin.strip() for origin in v.split(",") if origin.strip()]
        else:
            origins = ["http://localhost:3000"]

        production = "https://ai-english-teacher-web.onrender.com"
        if production not in origins:
            origins.append(production)
        return origins

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def normalize_database_url(cls, v: str) -> str:
        if isinstance(v, str) and v.startswith("postgres://"):
            return v.replace("postgres://", "postgresql+asyncpg://", 1)
        if isinstance(v, str) and v.startswith("postgresql://"):
            return v.replace("postgresql://", "postgresql+asyncpg://", 1)
        return v

    model_config = {"env_file": ".env", "extra": "ignore"}


@lru_cache
def get_settings() -> Settings:
    return Settings()
