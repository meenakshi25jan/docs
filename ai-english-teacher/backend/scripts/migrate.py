"""Run SQL migrations against PostgreSQL on startup."""

import asyncio
import os
import sys
from pathlib import Path

import asyncpg


def normalize_database_url(url: str) -> tuple[str, dict]:
    """Convert SQLAlchemy URL to asyncpg-compatible DSN + connect args."""
    from app.core.db_url import prepare_asyncpg_dsn

    return prepare_asyncpg_dsn(url)


async def run_migrations() -> None:
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        print("DATABASE_URL not set — skipping migrations")
        return

    database_url, connect_args = normalize_database_url(database_url)
    migrations_dir = Path(os.environ.get("MIGRATIONS_DIR", ""))
    if not migrations_dir or not migrations_dir.exists():
        migrations_dir = Path(__file__).resolve().parents[1] / "migrations"
    if not migrations_dir.exists():
        migrations_dir = Path(__file__).resolve().parents[2] / "database" / "migrations"

    if not migrations_dir.exists():
        print(f"Migrations directory not found: {migrations_dir}")
        return

    conn = await asyncpg.connect(database_url, timeout=30, **connect_args)
    try:
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS schema_migrations (
                filename TEXT PRIMARY KEY,
                applied_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
            )
        """)

        applied = {
            row["filename"]
            for row in await conn.fetch("SELECT filename FROM schema_migrations")
        }

        for sql_file in sorted(migrations_dir.glob("*.sql")):
            if sql_file.name in applied:
                print(f"  skip  {sql_file.name}")
                continue
            print(f"  apply {sql_file.name}")
            await conn.execute(sql_file.read_text())
            await conn.execute(
                "INSERT INTO schema_migrations (filename) VALUES ($1)",
                sql_file.name,
            )
        print("Migrations complete")
    finally:
        await conn.close()


if __name__ == "__main__":
    try:
        asyncio.run(run_migrations())
    except Exception as e:
        print(f"Migration error: {e}", file=sys.stderr)
        if os.environ.get("REQUIRE_MIGRATIONS", "false").lower() == "true":
            sys.exit(1)
