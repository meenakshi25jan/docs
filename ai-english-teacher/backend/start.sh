#!/bin/sh
set -e

echo "==> Running database migrations..."
python3 scripts/migrate.py

PORT="${PORT:-8000}"
echo "==> Starting API on port $PORT"
exec uvicorn app.main:app --host 0.0.0.0 --port "$PORT"
