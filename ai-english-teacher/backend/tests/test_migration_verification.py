"""Migration verification tests."""

import pytest

from app.services.production_readiness_service import EXPECTED_MIGRATIONS, _migrations_dir, verify_migrations
from unittest.mock import AsyncMock, MagicMock


class TestMigrationVerification:
    def test_expected_migrations_includes_007(self):
        assert "007_security_rls_hardening.sql" in EXPECTED_MIGRATIONS
        assert len(EXPECTED_MIGRATIONS) == 7

    def test_migrations_dir_exists(self):
        path = _migrations_dir()
        assert path.exists()
        for filename in EXPECTED_MIGRATIONS:
            assert (path / filename).exists()

    @pytest.mark.asyncio
    async def test_unexpected_migration_reported(self):
        db = AsyncMock()
        applied = list(EXPECTED_MIGRATIONS) + ["999_extra.sql"]
        db.execute = AsyncMock(return_value=[MagicMock(filename=f) for f in applied])
        result = await verify_migrations(db)
        assert "999_extra.sql" in result.unexpected
