#!/usr/bin/env bash
# Production API startup — SQL migrations (migrate.py) before uvicorn.
# MUST run under bash (Render /bin/sh is dash — no pipefail).
# Never set SKIP_MIGRATIONS=true in production (Render dashboard overrides blueprint).

set -Eeuo pipefail

on_err() {
  echo "ERROR: start.sh failed at line ${BASH_LINENO[0]} (exit ${?})"
  exit 1
}
trap on_err ERR

# --- Bash guard (Render may invoke ./start.sh via /bin/sh) ---
if [ -z "${BASH_VERSION:-}" ]; then
  echo "ERROR: Render is executing this script with /bin/sh (dash)."
  echo "Fix: set Start Command to: bash ./start.sh"
  echo "  shell=${SHELL:-unset} argv0=${0:-unset}"
  exit 1
fi

if ! command -v bash >/dev/null 2>&1; then
  echo "ERROR: bash is not available on PATH"
  exit 1
fi

ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"
export PYTHONPATH="${ROOT}${PYTHONPATH:+:${PYTHONPATH}}"

PORT="${PORT:-8000}"
ENVIRONMENT="${ENVIRONMENT:-production}"
SKIP_MIGRATIONS="${SKIP_MIGRATIONS:-false}"

resolve_git_commit() {
  if [ -n "${RENDER_GIT_COMMIT:-}" ]; then
    echo "$RENDER_GIT_COMMIT"
    return
  fi
  if [ -n "${GITHUB_SHA:-}" ]; then
    echo "$GITHUB_SHA"
    return
  fi
  if command -v git >/dev/null 2>&1 && git rev-parse HEAD >/dev/null 2>&1; then
    git rev-parse HEAD
    return
  fi
  echo "unknown"
}

GIT_COMMIT="$(resolve_git_commit)"

echo "==> start.sh bootstrap"
echo "==> Environment: ${ENVIRONMENT}"
echo "==> SKIP_MIGRATIONS=${SKIP_MIGRATIONS}"
echo "==> Git commit: ${GIT_COMMIT}"
echo "==> Shell: ${SHELL:-unset} | BASH_VERSION=${BASH_VERSION}"
echo "==> argv0: ${0}"
echo "==> Working directory: $(pwd)"
echo "==> PATH=${PATH}"
echo "==> PYTHONPATH=${PYTHONPATH}"
echo "==> Python executable: $(command -v python3)"
python3 --version
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
  echo "==> DATABASE_URL is set (host redacted)"
  if [ "$ENVIRONMENT" = "production" ] && [ -z "${OPENAI_API_KEY:-}" ]; then
    echo "ERROR: OPENAI_API_KEY is required in production (Groq/OpenAI)."
    exit 1
  fi
  if [ -n "${OPENAI_API_KEY:-}" ]; then
    echo "==> OPENAI_API_KEY is set"
  else
    echo "WARN: OPENAI_API_KEY not set (non-production)"
  fi
  echo "==> Running database migrations (python -m scripts.migrate)..."
  export REQUIRE_MIGRATIONS=true
  python3 -m scripts.migrate
  echo "==> Verifying migration tables and revision files..."
  python3 -m scripts.verify_migrations_applied
fi

echo "==> Launching FastAPI (uvicorn) on port ${PORT}..."
exec python3 -m uvicorn app.main:app --host 0.0.0.0 --port "$PORT"
