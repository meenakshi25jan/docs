#!/bin/sh
set -e

PORT="${PORT:-8000}"

# Run migrations in background so API starts even if DB is slow/unavailable
if [ "${SKIP_MIGRATIONS:-false}" != "true" ]; then
  echo "==> Running database migrations (background)..."
  python3 scripts/migrate.py || echo "==> Migration skipped or failed (non-fatal)"
fi

echo "==> Starting API on port $PORT"
exec python3 -m uvicorn app.main:app --host 0.0.0.0 --port "$PORT"
