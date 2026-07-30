#!/bin/sh
# Production API startup — migrations before uvicorn (never SKIP_MIGRATIONS=true in prod).
set -euo pipefail

PORT="${PORT:-8000}"
ENVIRONMENT="${ENVIRONMENT:-production}"

if [ "${SKIP_MIGRATIONS:-false}" = "true" ]; then
  echo "ERROR: SKIP_MIGRATIONS=true is not allowed in production deployments."
  echo "Set SKIP_MIGRATIONS=false in render.yaml and redeploy."
  if [ "$ENVIRONMENT" = "production" ]; then
    exit 1
  fi
  echo "WARN: continuing without migrations (non-production only)"
else
  if [ -z "${DATABASE_URL:-}" ]; then
    echo "ERROR: DATABASE_URL is required to run migrations."
    exit 1
  fi
  echo "==> Validating DATABASE_URL is set"
  echo "==> Running database migrations (synchronous)..."
  python3 scripts/migrate.py
  echo "==> Verifying migration tables..."
  python3 scripts/verify_migrations_applied.py
fi

echo "==> Starting API on port $PORT"
exec python3 -m uvicorn app.main:app --host 0.0.0.0 --port "$PORT"
