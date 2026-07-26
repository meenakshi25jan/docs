#!/usr/bin/env bash
# =============================================================================
# Universal Project Advisor - Linux/macOS launcher
# Detects your OS and prints tailored setup suggestions for ANY project.
#
# Usage:
#   ./scripts/advise.sh                    # General advice
#   ./scripts/advise.sh web                # Web project advice
#   ./scripts/advise.sh ai                 # AI project advice
#   ./scripts/advise.sh --json api         # JSON output
# =============================================================================

set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_DIR"

PROJECT_TYPE="${1:-general}"
JSON_FLAG=""

# Handle --json flag
if [[ "${1:-}" == "--json" ]]; then
  JSON_FLAG="--json"
  PROJECT_TYPE="${2:-general}"
elif [[ "${2:-}" == "--json" ]]; then
  JSON_FLAG="--json"
fi

# Use venv Python if available
if [ -f ".venv/bin/python" ]; then
  PYTHON=".venv/bin/python"
else
  PYTHON="python3"
fi

echo "[INFO] Running Project Advisor for: $PROJECT_TYPE"
echo "[INFO] Python: $PYTHON"
echo ""

$PYTHON scripts/project-advisor.py --project-type "$PROJECT_TYPE" $JSON_FLAG
