#!/usr/bin/env bash
# Production startup for Render and Docker.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"
export PYTHONPATH="${ROOT}${PYTHONPATH:+:${PYTHONPATH}}"

PORT="${PORT:-8000}"

echo "==> Running Alembic migrations"
alembic upgrade head

echo "==> Starting FastAPI on port ${PORT}"
exec uvicorn app.main:app --host 0.0.0.0 --port "$PORT"
