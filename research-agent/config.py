"""Application configuration loaded from environment variables."""

from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path
from typing import Literal

from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent


class Settings(BaseSettings):
    """Central configuration for the research agent."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Application
    app_name: str = "Research Agent"
    app_version: str = "1.0.0"
    debug: bool = False
    data_dir: Path = Field(default=BASE_DIR / "data")
    reports_dir: Path = Field(default=BASE_DIR / "reports")
    logs_dir: Path = Field(default=BASE_DIR / "logs")

    # Database
    database_url: str = Field(
        default=f"sqlite+aiosqlite:///{BASE_DIR / 'data' / 'research_agent.db'}"
    )
    database_echo: bool = False

    # Crawler
    default_depth: int = 2
    default_max_pages: int = 100
    request_timeout: float = 30.0
    max_retries: int = 3
    retry_backoff: float = 1.5
    rate_limit_delay: float = 0.5
    max_concurrent_requests: int = 10
    max_concurrent_playwright: int = 3
    respect_robots_txt: bool = True
    use_playwright: bool = True
    follow_redirects: bool = True
    max_content_size_mb: int = 10

    # Search
    search_provider: Literal["duckduckgo", "google", "bing"] = "duckduckgo"
    google_api_key: str | None = None
    google_cse_id: str | None = None
    bing_api_key: str | None = None
    search_max_results: int = 50

    # AI / LLM
    llm_provider: Literal["openai", "ollama", "local", "none"] = "none"
    openai_api_key: str | None = None
    openai_model: str = "gpt-4o-mini"
    openai_base_url: str | None = None
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.2"
    local_llm_url: str | None = None
    local_llm_model: str = "local"

    # Embeddings
    embedding_model: str = "all-MiniLM-L6-v2"
    chroma_persist_dir: Path = Field(default=BASE_DIR / "data" / "chroma")
    chroma_collection: str = "research_pages"

    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_key: str | None = None
    cors_origins: list[str] = Field(default_factory=lambda: ["*"])

    # User agents for rotation
    user_agents: list[str] = Field(
        default_factory=lambda: [
            (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            ),
            (
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            ),
            (
                "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            ),
            (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) "
                "Gecko/20100101 Firefox/121.0"
            ),
            (
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:121.0) "
                "Gecko/20100101 Firefox/121.0"
            ),
        ]
    )

    def ensure_directories(self) -> None:
        """Create required data directories."""
        for directory in (
            self.data_dir,
            self.reports_dir,
            self.logs_dir,
            self.chroma_persist_dir,
        ):
            directory.mkdir(parents=True, exist_ok=True)


@lru_cache
def get_settings() -> Settings:
    """Return cached settings instance."""
    settings = Settings()
    settings.ensure_directories()
    return settings
