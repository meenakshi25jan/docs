"""Run SQL migrations against PostgreSQL on startup (not Alembic — plain *.sql files)."""

from __future__ import annotations

import asyncio
import os
import sys
from pathlib import Path

# Bootstrap before any `app` imports (scripts/migrate.py is not run as a package entry).
_BACKEND = Path(__file__).resolve().parents[1]
if str(_BACKEND) not in sys.path:
    sys.path.insert(0, str(_BACKEND))

from scripts.bootstrap_path import (
    ensure_backend_on_sys_path,
    print_runtime_diagnostics,
    resolve_migrations_dir,
)

ensure_backend_on_sys_path()

import asyncpg


def normalize_database_url(url: str) -> tuple[str, dict]:
    """Convert SQLAlchemy URL to asyncpg-compatible DSN + connect args."""
    from app.core.db_url import prepare_asyncpg_dsn

    return prepare_asyncpg_dsn(url)


def should_fail_on_error() -> bool:
    env = os.environ.get("ENVIRONMENT", "").lower()
    require = os.environ.get("REQUIRE_MIGRATIONS", "false").lower()
    return env == "production" or require in ("1", "true", "yes")


async def run_migrations() -> None:
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        print("DATABASE_URL not set — skipping migrations")
        if should_fail_on_error():
            raise RuntimeError("DATABASE_URL required for migrations in production")
        return

    migrations_dir = resolve_migrations_dir()
    if migrations_dir is None:
        msg = "Migrations directory not found"
        print(msg)
        if should_fail_on_error():
            raise RuntimeError(msg)
        return

    database_url, connect_args = normalize_database_url(database_url)
    print(f"Database connected (migrations dir: {migrations_dir})")

    conn = await asyncpg.connect(database_url, timeout=30, **connect_args)
    try:
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS schema_migrations (
                filename TEXT PRIMARY KEY,
                applied_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
            )
        """)

        applied = {
            row["filename"] for row in await conn.fetch("SELECT filename FROM schema_migrations")
        }

        pending = sorted(f for f in migrations_dir.glob("*.sql") if f.name not in applied)
        print(f"Pending migrations: {len(pending)}")
        if pending:
            for p in pending:
                print(f"  pending {p.name}")

        for sql_file in sorted(migrations_dir.glob("*.sql")):
            if sql_file.name in applied:
                print(f"  skip  {sql_file.name}")
                continue
            print(f"Applying migration: {sql_file.name}")
            await conn.execute(sql_file.read_text())
            await conn.execute(
                "INSERT INTO schema_migrations (filename) VALUES ($1)",
                sql_file.name,
            )
            print(f"  applied {sql_file.name}")
        print("Migration complete")
    finally:
        await conn.close()


if __name__ == "__main__":
    print_runtime_diagnostics("migrate.py")
    try:
        asyncio.run(run_migrations())
    except Exception as e:
        print(f"Migration error: {e}", file=sys.stderr)
        if should_fail_on_error():
            sys.exit(1)
