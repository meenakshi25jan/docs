from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "Prompt Studio"
    app_version: str = "1.0.0"
    debug: bool = False

    # OpenAI-compatible API (OpenAI, Azure OpenAI, local LLM gateways, etc.)
    openai_api_key: str = ""
    openai_base_url: str = "https://api.openai.com/v1"
    openai_model: str = "gpt-4o"
    openai_temperature: float = 0.4
    openai_max_tokens: int = 4096
    openai_timeout_seconds: float = 120.0

    # Server
    host: str = "0.0.0.0"
    port: int = 8080
    cors_origins: str = "*"

    # Paths
    prompts_dir: Path = Path(__file__).resolve().parent / "prompts"
    static_dir: Path = Path(__file__).resolve().parent / "static"

    @property
    def cors_origin_list(self) -> list[str]:
        if self.cors_origins.strip() == "*":
            return ["*"]
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
