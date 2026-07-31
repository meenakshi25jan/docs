"""Tests for migration script package resolution (Render startup)."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

BACKEND = Path(__file__).resolve().parents[1]


def test_migrate_imports_app_from_any_cwd() -> None:
    """migrate.py must resolve `app` without ModuleNotFoundError."""
    env = {
        **dict(__import__("os").environ),
        "PYTHONPATH": str(BACKEND),
        "DATABASE_URL": "",  # skip DB — import path is tested first
    }
    result = subprocess.run(
        [sys.executable, "-c", "from scripts.bootstrap_path import ensure_backend_on_sys_path; "
         "ensure_backend_on_sys_path(); from app.core.db_url import prepare_asyncpg_dsn; "
         "print('ok')"],
        cwd="/tmp",
        env=env,
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert result.returncode == 0, result.stderr
    assert "ok" in result.stdout


def test_migration_files_count() -> None:
    from scripts.bootstrap_path import list_migration_files

    files = list_migration_files()
    assert len(files) == 8
    names = [f.name for f in files]
    assert names == [
        "001_initial_schema.sql",
        "002_pgvector.sql",
        "003_auth_rls.sql",
        "004_fix_rls_policies.sql",
        "005_knowledge_and_voice.sql",
        "006_curriculum_intelligence.sql",
        "007_security_rls_hardening.sql",
        "008_fix_knowledge_chunks_seed.sql",
    ]
