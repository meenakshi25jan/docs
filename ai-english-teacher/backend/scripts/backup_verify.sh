#!/usr/bin/env bash
# Non-destructive Neon/PostgreSQL backup readiness checks.
#
# Verifies DATABASE_URL connectivity, schema_migrations readability,
# tenant count query, and a sample health-style query.
#
# Usage (Neon):
#   export DATABASE_URL='postgresql://user:pass@host/db?sslmode=require'
#   ./scripts/backup_verify.sh
#
# Exit codes: 0 success, 1 failure

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"

if [[ -z "${DATABASE_URL:-}" ]]; then
  echo "FAIL: DATABASE_URL is not set"
  exit 1
fi

echo "backup_verify: DATABASE_URL present"
echo "backup_verify: probing database (non-destructive reads only)"

python3 - <<'PY' "${DATABASE_URL}"
import os
import sys

url = sys.argv[1] if len(sys.argv) > 1 else os.environ.get("DATABASE_URL", "")
if not url:
    print("FAIL: DATABASE_URL missing")
    sys.exit(1)

# Normalize asyncpg URLs for psycopg if needed
sync_url = url.replace("postgresql+asyncpg://", "postgresql://")

try:
  import psycopg
except ImportError:
  try:
    import psycopg2 as psycopg
    connect = lambda u: psycopg.connect(u)
    cursor_ctx = lambda conn: conn.cursor()
  except ImportError:
    print("FAIL: install psycopg or psycopg2-binary to run backup_verify.sh")
    sys.exit(1)
else:
  connect = lambda u: psycopg.connect(u)
  cursor_ctx = lambda conn: conn.cursor()

errors = []

try:
  with connect(sync_url) as conn:
    with cursor_ctx(conn) as cur:
      cur.execute("SELECT COUNT(*) FROM schema_migrations")
      migration_count = cur.fetchone()[0]
      print(f"OK: schema_migrations readable (count={migration_count})")

      cur.execute("SELECT COUNT(*) FROM tenants")
      tenant_count = cur.fetchone()[0]
      print(f"OK: tenants readable (count={tenant_count})")

      cur.execute("SELECT 1")
      health = cur.fetchone()[0]
      if health != 1:
        errors.append("health query returned unexpected value")
      else:
        print("OK: sample health query (SELECT 1)")
except Exception as exc:
  print(f"FAIL: database probe — {type(exc).__name__}: {exc}")
  sys.exit(1)

if errors:
  for e in errors:
    print(f"FAIL: {e}")
  sys.exit(1)

print("backup_verify: all checks passed")
PY

exit 0
