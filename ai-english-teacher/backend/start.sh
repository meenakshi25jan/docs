#!/bin/sh
# Production API startup — SQL migrations (migrate.py) before uvicorn.
# Never set SKIP_MIGRATIONS=true in production (Render dashboard overrides blueprint).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"
export PYTHONPATH="${ROOT}${PYTHONPATH:+:${PYTHONPATH}}"

PORT="${PORT:-8000}"
ENVIRONMENT="${ENVIRONMENT:-production}"
SKIP_MIGRATIONS="${SKIP_MIGRATIONS:-false}"

echo "==> Environment: ${ENVIRONMENT}"
echo "==> SKIP_MIGRATIONS=${SKIP_MIGRATIONS}"
echo "==> Working directory: $(pwd)"
echo "==> Python executable: $(command -v python3)"
python3 --version
echo "==> PYTHONPATH=${PYTHONPATH}"
python3 -c "import sys; print('==> sys.path:', sys.path[:8])"

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
  echo "==> DATABASE_URL is set"
  echo "==> Running database migrations (python -m scripts.migrate)..."
  export REQUIRE_MIGRATIONS=true
  python3 -m scripts.migrate
  echo "==> Verifying migration tables and revision files..."
  python3 -m scripts.verify_migrations_applied
fi

echo "==> Launching FastAPI (uvicorn) on port ${PORT}..."
exec python3 -m uvicorn app.main:app --host 0.0.0.0 --port "$PORT"
