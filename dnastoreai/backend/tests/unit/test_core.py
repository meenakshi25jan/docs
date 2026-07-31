"""Unit tests for core config and exceptions."""

from pathlib import Path

from dnastoreai.core.config import Settings, ensure_directories, get_settings
from dnastoreai.core.exceptions import (
    ArchiveNotFoundError,
    CompressionError,
    DNAStoreAIError,
)


class TestConfig:
    def test_settings_defaults(self):
        s = Settings()
        assert s.app_name == "DNAStoreAI"
        assert s.default_encoding == "gc_balanced"

    def test_effective_database_url(self):
        s = Settings()
        assert "sqlite" in s.effective_database_url

    def test_postgres_url(self):
        s = Settings(postgres_url="postgresql+asyncpg://user:pass@host/db")
        assert s.effective_database_url == "postgresql+asyncpg://user:pass@host/db"

    def test_ensure_directories(self, tmp_path):
        s = Settings(data_dir=tmp_path / "data", archive_dir=tmp_path / "archive")
        result = ensure_directories(s)
        assert result.archive_dir.exists()

    def test_get_settings_cached(self):
        get_settings.cache_clear()
        s1 = get_settings()
        s2 = get_settings()
        assert s1 is s2


class TestExceptions:
    def test_base_error(self):
        e = DNAStoreAIError("test", "CODE")
        assert e.code == "CODE"
        assert str(e) == "test"

    def test_archive_not_found(self):
        e = ArchiveNotFoundError("abc")
        assert e.code == "ARCHIVE_NOT_FOUND"

    def test_compression_error(self):
        e = CompressionError("fail")
        assert e.code == "COMPRESSION_ERROR"
