#!/usr/bin/env bash
# =============================================================================
# CREATE PROJECT - Linux / macOS
# One command to create and set up the entire Research Agent project.
#
# Usage:
#   chmod +x scripts/create-project.sh
#   ./scripts/create-project.sh
# =============================================================================

set -euo pipefail

echo ""
echo "╔══════════════════════════════════════════════════════════╗"
echo "║         RESEARCH AGENT - CREATE PROJECT                  ║"
echo "║         Setting up everything for you...                 ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_DIR"

# --- Detect OS ---
OS_NAME="Linux"
if [[ "$(uname -s)" == "Darwin" ]]; then
  OS_NAME="macOS"
fi
echo "[1/6] Detected OS: $OS_NAME"

# --- Check Python ---
echo "[2/6] Checking Python..."
if ! command -v python3 &>/dev/null; then
  echo ""
  echo "ERROR: Python 3 is not installed."
  if [[ "$OS_NAME" == "macOS" ]]; then
    echo "  Fix: brew install python@3.12"
    echo "  Or:  https://www.python.org/downloads/"
  else
    echo "  Fix: sudo apt install -y python3 python3-pip python3-venv"
    echo "  Or:  https://www.python.org/downloads/"
  fi
  exit 1
fi
echo "       Found: $(python3 --version)"

# --- Run full setup ---
echo "[3/6] Installing dependencies (may take 3-5 minutes)..."
chmod +x scripts/setup-linux.sh scripts/advise.sh scripts/start-api.sh 2>/dev/null || true
if [[ "$OS_NAME" == "macOS" ]] && [[ -f "scripts/setup-mac.sh" ]]; then
  ./scripts/setup-mac.sh
else
  ./scripts/setup-linux.sh
fi

# --- Show OS-specific advice ---
echo ""
echo "[4/6] Running OS advisor..."
./scripts/advise.sh ai || true

# --- Verify project structure ---
echo ""
echo "[5/6] Verifying project structure..."
for dir in data reports logs; do
  mkdir -p "$dir"
  echo "       ✓ $dir/"
done
[[ -f ".env" ]] && echo "       ✓ .env" || echo "       ✗ .env missing"
[[ -d ".venv" ]] && echo "       ✓ .venv/" || echo "       ✗ .venv missing"

# --- Done ---
echo ""
echo "[6/6] Project created successfully!"
echo ""
echo "╔══════════════════════════════════════════════════════════╗"
echo "║  PROJECT READY! Run these commands:                      ║"
echo "╠══════════════════════════════════════════════════════════╣"
echo "║                                                          ║"
echo "║  source .venv/bin/activate                               ║"
echo "║                                                          ║"
echo "║  # Your first research:                                  ║"
echo "║  python -m app.main search \\                            ║"
echo "║    --query \"Artificial Intelligence\" \\                   ║"
echo "║    --depth 1 --pages 3                                   ║"
echo "║                                                          ║"
echo "║  # Start web interface:                                  ║"
echo "║  python -m app.main serve                                ║"
echo "║  # Then open: http://localhost:8000/docs                 ║"
echo "║                                                          ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""
echo "Full guide: docs/CREATE_PROJECT.md"
echo ""
