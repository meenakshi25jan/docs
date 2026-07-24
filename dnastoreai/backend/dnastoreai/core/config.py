"""Application configuration with dependency injection support."""

from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Central configuration for DNAStoreAI platform."""

    model_config = SettingsConfigDict(env_file=".env", env_prefix="DNASTORE_", extra="ignore")

    app_name: str = "DNAStoreAI"
    app_version: str = "0.1.0"
    debug: bool = False
    api_prefix: str = "/api/v1"

    # Storage
    data_dir: Path = Field(default=Path("./data"))
    archive_dir: Path = Field(default=Path("./data/archive"))
    upload_dir: Path = Field(default=Path("./data/uploads"))
    experiment_dir: Path = Field(default=Path("./data/experiments"))

    # Database
    database_url: str = "sqlite+aiosqlite:///./data/dnastoreai.db"
    postgres_url: str | None = None

    # Vector DB
    chroma_persist_dir: Path = Field(default=Path("./data/chroma"))
    vector_db_enabled: bool = True

    # Pipeline defaults
    default_block_size: int = 4096
    default_compression: Literal["gzip", "zlib", "lzma"] = "gzip"
    default_encoding: Literal["basic", "rotating", "gc_balanced", "custom"] = "gc_balanced"
    default_ecc: Literal["reed_solomon", "bch", "ldpc", "fountain"] = "reed_solomon"
    default_sequencing: Literal["illumina", "nanopore", "pacbio"] = "illumina"

    # Simulation defaults
    substitution_rate: float = 0.001
    insertion_rate: float = 0.0001
    deletion_rate: float = 0.0001
    degradation_temperature: float = 25.0
    degradation_humidity: float = 50.0
    degradation_time_years: float = 1.0

    @property
    def effective_database_url(self) -> str:
        return self.postgres_url or self.database_url


@lru_cache
def get_settings() -> Settings:
    """Cached settings singleton for dependency injection."""
    return Settings()


def ensure_directories(settings: Settings | None = None) -> Settings:
    """Create required data directories."""
    cfg = settings or get_settings()
    for path in (cfg.data_dir, cfg.archive_dir, cfg.upload_dir, cfg.experiment_dir, cfg.chroma_persist_dir):
        path.mkdir(parents=True, exist_ok=True)
    return cfg
