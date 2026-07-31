#!/usr/bin/env python3
"""Verify expected migration tables exist after migrate.py runs."""

from __future__ import annotations

import asyncio
import os
import sys
from pathlib import Path

_BACKEND = Path(__file__).resolve().parents[1]
if str(_BACKEND) not in sys.path:
    sys.path.insert(0, str(_BACKEND))

from scripts.bootstrap_path import ensure_backend_on_sys_path, print_runtime_diagnostics

ensure_backend_on_sys_path()

EXPECTED_TABLES = [
    "schema_migrations",
    "users",
    "learner_profiles",
    "conversations",
    "conversation_messages",
    "voice_analyses",
    "lesson_completions",
    "revision_schedule",
    "knowledge_chunks",
]

EXPECTED_MIGRATION_FILES = [
    "001_initial_schema.sql",
    "002_pgvector.sql",
    "003_auth_rls.sql",
    "004_fix_rls_policies.sql",
    "005_knowledge_and_voice.sql",
    "006_curriculum_intelligence.sql",
    "007_security_rls_hardening.sql",
    "008_fix_knowledge_chunks_seed.sql",
]


async def verify() -> list[str]:
    url = os.environ.get("DATABASE_URL")
    if not url:
        return ["DATABASE_URL not set"]

    errors: list[str] = []
    import asyncpg
    from app.core.db_url import prepare_asyncpg_dsn

    dsn, connect_args = prepare_asyncpg_dsn(url)
    conn = await asyncpg.connect(dsn, timeout=30, **connect_args)
    try:
        for table in EXPECTED_TABLES:
            row = await conn.fetchval(
                "SELECT EXISTS (SELECT 1 FROM information_schema.tables "
                "WHERE table_schema = 'public' AND table_name = $1)",
                table,
            )
            if not row:
                errors.append(f"missing table: {table}")

        applied = await conn.fetch(
            "SELECT filename, applied_at FROM schema_migrations ORDER BY filename"
        )
        filenames = {r["filename"] for r in applied}
        missing = [m for m in EXPECTED_MIGRATION_FILES if m not in filenames]
        if missing:
            errors.append(f"missing applied migrations: {missing}")
        print(f"Applied migrations: {len(filenames)}", flush=True)
        for row in applied:
            print(f"  {row['filename']} @ {row['applied_at']}", flush=True)
    finally:
        await conn.close()
    return errors


def main() -> int:
    print_runtime_diagnostics("verify_migrations_applied.py")
    errors = asyncio.run(verify())
    if errors:
        print("Migration verification FAILED:", flush=True)
        for e in errors:
            print(f"  - {e}", flush=True)
        return 1
    print("Migration verification passed", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
