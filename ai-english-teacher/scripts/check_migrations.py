#!/usr/bin/env python3
"""Check SQL migrations on disk and optionally against Neon (schema_migrations)."""

from __future__ import annotations

import asyncio
import os
import sys
from pathlib import Path

EXPECTED = [
    "001_initial_schema.sql",
    "002_pgvector.sql",
    "003_auth_rls.sql",
    "004_fix_rls_policies.sql",
    "005_knowledge_and_voice.sql",
    "006_curriculum_intelligence.sql",
    "007_security_rls_hardening.sql",
]

REPO_ROOT = Path(__file__).resolve().parents[2]
MIGRATIONS_DIR = REPO_ROOT / "ai-english-teacher" / "database" / "migrations"


def check_on_disk() -> list[str]:
    errors: list[str] = []
    if not MIGRATIONS_DIR.is_dir():
        return [f"migrations dir missing: {MIGRATIONS_DIR}"]
    on_disk = sorted(p.name for p in MIGRATIONS_DIR.glob("*.sql"))
    for name in EXPECTED:
        if name not in on_disk:
            errors.append(f"missing file on disk: {name}")
    extra = [n for n in on_disk if n not in EXPECTED]
    if extra:
        errors.append(f"unexpected migration files: {extra}")
    return errors


async def check_database() -> list[str]:
    url = os.environ.get("DATABASE_URL")
    if not url:
        print("DATABASE_URL not set — skipping database migration check")
        return []

    errors: list[str] = []
    try:
        import asyncpg
        from app.core.db_url import prepare_asyncpg_dsn
    except ImportError as exc:
        return [f"cannot import migration deps: {exc}"]

    dsn, connect_args = prepare_asyncpg_dsn(url)
    conn = await asyncpg.connect(dsn, timeout=30, **connect_args)
    try:
        rows = await conn.fetch("SELECT filename FROM schema_migrations ORDER BY filename")
        applied = {r["filename"] for r in rows}
        missing = [m for m in EXPECTED if m not in applied]
        if missing:
            errors.append(f"database missing migrations: {missing}")
        print(f"Applied migrations: {len(applied)}")
    finally:
        await conn.close()
    return errors


async def async_main() -> int:
    errors = check_on_disk()
    if errors:
        print("On-disk migration check FAILED:")
        for e in errors:
            print(f"  - {e}")
        return 1
    print(f"On-disk migrations OK ({len(EXPECTED)} expected files)")

    db_errors = await check_database()
    if db_errors:
        print("Database migration check FAILED:")
        for e in db_errors:
            print(f"  - {e}")
        return 1
    return 0


def main() -> int:
    # Allow running from backend with app on path
    backend = Path(__file__).resolve().parents[1]
    if str(backend) not in sys.path:
        sys.path.insert(0, str(backend))
    return asyncio.run(async_main())


if __name__ == "__main__":
    sys.exit(main())
