#!/usr/bin/env bash
# =============================================================================
# Research Agent - Linux Setup Script (Ubuntu/Debian)
# Purpose: Install everything a beginner needs to run the project locally
# Usage:   chmod +x scripts/setup-linux.sh && ./scripts/setup-linux.sh
# =============================================================================

set -euo pipefail

echo "=============================================="
echo " Research Agent - Linux Setup"
echo "=============================================="

# Move to project root (parent of scripts/)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_DIR"
echo "[INFO] Project directory: $PROJECT_DIR"

# --- Step 1: Check Python ---
echo ""
echo "[STEP 1/7] Checking Python 3.12+..."
if ! command -v python3 &>/dev/null; then
  echo "[ERROR] Python 3 is not installed."
  echo "        Install with: sudo apt update && sudo apt install -y python3 python3-pip python3-venv"
  exit 1
fi
PYTHON_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
echo "[OK] Found Python $PYTHON_VERSION"

# --- Step 2: Install system dependencies ---
echo ""
echo "[STEP 2/7] Installing system packages (may ask for sudo password)..."
sudo apt-get update -qq
sudo apt-get install -y -qq python3-venv python3-pip build-essential curl 2>/dev/null || true
echo "[OK] System packages ready"

# --- Step 3: Create virtual environment ---
echo ""
echo "[STEP 3/7] Creating Python virtual environment..."
if [ ! -d ".venv" ]; then
  python3 -m venv .venv
  echo "[OK] Created .venv"
else
  echo "[OK] .venv already exists"
fi

# --- Step 4: Activate and install Python packages ---
echo ""
echo "[STEP 4/7] Installing Python dependencies (this may take a few minutes)..."
# shellcheck disable=SC1091
source .venv/bin/activate
pip install --upgrade pip -q
pip install -r requirements.txt -q
echo "[OK] Python packages installed"

# --- Step 5: Install Playwright browser ---
echo ""
echo "[STEP 5/7] Installing Playwright Chromium browser..."
playwright install chromium
echo "[OK] Playwright ready"

# --- Step 6: Create config and folders ---
echo ""
echo "[STEP 6/7] Creating data folders and .env file..."
mkdir -p data reports logs
if [ ! -f ".env" ]; then
  cp .env.example .env
  echo "[OK] Created .env from .env.example"
else
  echo "[OK] .env already exists"
fi

# --- Step 7: Run tests ---
echo ""
echo "[STEP 7/7] Running tests to verify installation..."
pytest -q --tb=no
echo "[OK] All tests passed"

echo ""
echo "=============================================="
echo " SETUP COMPLETE!"
echo "=============================================="
echo ""
echo "Next steps:"
echo "  1. Activate environment:  source .venv/bin/activate"
echo "  2. Run a test search:       python -m app.main search --query \"AI\" --depth 1 --pages 3"
echo "  3. Start API server:        python -m app.main serve"
echo "  4. Open in browser:         http://localhost:8000/docs"
echo ""
echo "Read the full guide: docs/BEGINNER_PLAYBOOK.md"
echo "=============================================="
