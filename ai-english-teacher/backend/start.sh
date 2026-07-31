#!/bin/sh
# Production API startup — SQL migrations (migrate.py) before uvicorn.
# Never set SKIP_MIGRATIONS=true in production (Render dashboard overrides blueprint).
set -euo pipefail

PORT="${PORT:-8000}"
ENVIRONMENT="${ENVIRONMENT:-production}"
SKIP_MIGRATIONS="${SKIP_MIGRATIONS:-false}"

echo "==> Environment: ${ENVIRONMENT}"
echo "==> SKIP_MIGRATIONS=${SKIP_MIGRATIONS}"

if [ "${SKIP_MIGRATIONS}" = "true" ]; then
  echo "ERROR: SKIP_MIGRATIONS=true is not allowed in production deployments."
  echo "Fix: Set SKIP_MIGRATIONS=false in render.yaml and redeploy."
  echo "If render.yaml already has false, delete the SKIP_MIGRATIONS row in"
  echo "Render Dashboard → ai-english-teacher-api → Environment (dashboard overrides blueprint)."
  if [ "$ENVIRONMENT" = "production" ]; then
    exit 1
  fi
  echo "WARN: continuing without migrations (non-production only)"
else
  if [ -z "${DATABASE_URL:-}" ]; then
    echo "ERROR: DATABASE_URL is required to run migrations."
    exit 1
  fi
  echo "==> Database URL configured"
  echo "==> Running database migrations (SQL via scripts/migrate.py)..."
  export REQUIRE_MIGRATIONS=true
  python3 scripts/migrate.py
  echo "==> Verifying migration tables and revision files..."
  python3 scripts/verify_migrations_applied.py
  echo "==> Migration verification complete"
fi

echo "==> Launching FastAPI (uvicorn) on port ${PORT}..."
exec python3 -m uvicorn app.main:app --host 0.0.0.0 --port "$PORT"
