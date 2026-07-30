"""RLS migration and diagnostics tests."""

from pathlib import Path

import pytest

from app.services.security_service import CRITICAL_RLS_TABLES


class TestMigration007:
    def test_migration_file_exists(self):
        root = Path(__file__).resolve().parents[2]
        migration = root / "database" / "migrations" / "007_security_rls_hardening.sql"
        assert migration.exists()

    def test_migration_covers_critical_tables(self):
        root = Path(__file__).resolve().parents[2]
        migration = root / "database" / "migrations" / "007_security_rls_hardening.sql"
        text = migration.read_text()
        for table in (
            "conversation_messages",
            "assessment_results",
            "voice_analyses",
            "learner_memories",
        ):
            assert table in text

    def test_critical_rls_manifest_includes_child_tables(self):
        assert "conversation_messages" in CRITICAL_RLS_TABLES
        assert "assessment_results" in CRITICAL_RLS_TABLES


class TestRLSDiagnosticsService:
    @pytest.mark.asyncio
    async def test_rls_diagnostics_returns_table_coverage(self, admin_client):
        from app.services.security_service import get_rls_diagnostics

        result = await get_rls_diagnostics(admin_client.mock_db, admin_client.mock_user)
        names = {t.table_name for t in result.tables}
        for table in CRITICAL_RLS_TABLES:
            assert table in names
