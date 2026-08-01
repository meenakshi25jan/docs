#!/usr/bin/env bash
# Alembic round-trip against ephemeral Postgres (CI migration gate).
set -euo pipefail

cd "$(dirname "$0")/../backend"

export JWT_SECRET="${JWT_SECRET:-ci-migration-secret}"
export DATABASE_URL="${DATABASE_URL:?DATABASE_URL is required}"

echo "==> alembic upgrade head"
alembic upgrade head

echo "==> alembic downgrade -1"
alembic downgrade -1

echo "==> alembic upgrade head (again)"
alembic upgrade head

echo "OK: migration round-trip succeeded"
