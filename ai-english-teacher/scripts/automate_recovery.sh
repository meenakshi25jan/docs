#!/usr/bin/env bash
# One-command local production recovery (requires env secrets — see AUTOMATED_RECOVERY.md).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

echo "=== 1. Validate configuration ==="
python3 scripts/validate_render_config.py
python3 scripts/validate_environment.py

echo "=== 2. Database migrations (if DATABASE_URL set) ==="
if [ -n "${DATABASE_URL:-}" ]; then
  cd backend
  pip install -q -r requirements-render.txt
  python3 scripts/migrate.py
  python3 scripts/verify_migrations_applied.py
  cd ..
else
  echo "SKIP: export DATABASE_URL to run migrations locally"
fi

echo "=== 3. Trigger Render deploys ==="
export CLEAR_WEB_BUILD_CACHE="${CLEAR_WEB_BUILD_CACHE:-true}"
export DEPLOY_TARGET="${DEPLOY_TARGET:-both}"
python3 scripts/trigger_render_deploy.py || {
  echo "Deploy hooks/API not configured — use Render Dashboard Manual Deploy + Clear cache"
}

echo "=== 4. Wait for API ==="
export WAIT_BASE_URL="${DEPLOY_API_URL:-https://ai-english-teacher-api.onrender.com}"
export WAIT_PATHS="/health/live,/health"
export WAIT_TIMEOUT="${WAIT_TIMEOUT:-600}"
python3 scripts/wait_for_healthy.py || echo "WARN: API not healthy yet"

echo "=== 5. Wait for Web (grammar-class) ==="
export WAIT_BASE_URL="${DEPLOY_WEB_URL:-https://ai-english-teacher-web.onrender.com}"
export WAIT_PATHS="/,/grammar-class"
python3 scripts/wait_for_healthy.py || echo "WARN: Web not healthy yet"

echo "=== 6. Post-deploy verification ==="
export DEPLOY_WEB_URL="${DEPLOY_WEB_URL:-https://ai-english-teacher-web.onrender.com}"
export DEPLOY_API_URL="${DEPLOY_API_URL:-https://ai-english-teacher-api.onrender.com}"
python3 scripts/post_deploy_verify.py

echo "=== Recovery complete ==="
