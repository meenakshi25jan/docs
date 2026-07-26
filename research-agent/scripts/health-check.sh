#!/usr/bin/env bash
# Health check for the Research Agent API
# Usage: ./scripts/health-check.sh [url]
# Example: ./scripts/health-check.sh http://localhost:8000

URL="${1:-http://localhost:8000}"
HEALTH_URL="$URL/health"

echo "[INFO] Checking: $HEALTH_URL"

if curl -sf "$HEALTH_URL" > /dev/null; then
  echo "[OK] API is healthy"
  curl -s "$HEALTH_URL" | python3 -m json.tool 2>/dev/null || curl -s "$HEALTH_URL"
  exit 0
else
  echo "[ERROR] API is not responding at $HEALTH_URL"
  echo "        Make sure the server is running: ./scripts/start-api.sh"
  exit 1
fi
