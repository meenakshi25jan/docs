#!/usr/bin/env bash
# Emergency recovery checklist — run after failed deploy or disaster.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

echo "=== 1. Validate configuration ==="
python3 scripts/validate_render_config.py
python3 scripts/validate_environment.py

echo "=== 2. Diagnose production ==="
python3 scripts/diagnose_deployment.py || true

if [ -n "${DATABASE_URL:-}" ]; then
  echo "=== 3. Run migrations ==="
  cd backend && python3 scripts/migrate.py
  python3 scripts/verify_migrations_applied.py
  cd ..
else
  echo "=== 3. Skip migrations (DATABASE_URL not set) ==="
fi

echo "=== 4. Post-deploy verification ==="
python3 scripts/post_deploy_verify.py

echo "=== Recovery checks complete ==="
