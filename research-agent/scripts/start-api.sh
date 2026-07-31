#!/usr/bin/env bash
# Starts the Research Agent API server
# Usage: ./scripts/start-api.sh [port]

set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$(dirname "$SCRIPT_DIR")"

PORT="${1:-8000}"

if [ ! -d ".venv" ]; then
  echo "[ERROR] Virtual environment not found. Run setup script first."
  exit 1
fi

source .venv/bin/activate
echo "[INFO] Starting API on http://localhost:$PORT"
echo "[INFO] API docs: http://localhost:$PORT/docs"
python -m app.main serve --host 0.0.0.0 --port "$PORT"
