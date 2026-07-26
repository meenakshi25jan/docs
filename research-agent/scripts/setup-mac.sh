#!/usr/bin/env bash
# =============================================================================
# Research Agent - macOS Setup Script
# Purpose: Install everything a beginner needs to run the project locally
# Usage:   chmod +x scripts/setup-mac.sh && ./scripts/setup-mac.sh
# Prerequisites: Install Homebrew from https://brew.sh if not installed
# =============================================================================

set -euo pipefail

echo "=============================================="
echo " Research Agent - macOS Setup"
echo "=============================================="

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_DIR"
echo "[INFO] Project directory: $PROJECT_DIR"

# --- Step 1: Check Homebrew ---
echo ""
echo "[STEP 1/7] Checking Homebrew..."
if ! command -v brew &>/dev/null; then
  echo "[ERROR] Homebrew is not installed."
  echo "        Install from: https://brew.sh"
  echo '        Run: /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"'
  exit 1
fi
echo "[OK] Homebrew found"

# --- Step 2: Install Python if needed ---
echo ""
echo "[STEP 2/7] Checking Python 3.12+..."
if ! command -v python3 &>/dev/null; then
  echo "[INFO] Installing Python via Homebrew..."
  brew install python@3.12
fi
PYTHON_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
echo "[OK] Found Python $PYTHON_VERSION"

# --- Step 3: Create virtual environment ---
echo ""
echo "[STEP 3/7] Creating Python virtual environment..."
if [ ! -d ".venv" ]; then
  python3 -m venv .venv
  echo "[OK] Created .venv"
else
  echo "[OK] .venv already exists"
fi

# --- Step 4: Install Python packages ---
echo ""
echo "[STEP 4/7] Installing Python dependencies..."
source .venv/bin/activate
pip install --upgrade pip -q
pip install -r requirements.txt -q
echo "[OK] Python packages installed"

# --- Step 5: Install Playwright ---
echo ""
echo "[STEP 5/7] Installing Playwright Chromium..."
playwright install chromium
echo "[OK] Playwright ready"

# --- Step 6: Create folders and .env ---
echo ""
echo "[STEP 6/7] Creating data folders and .env..."
mkdir -p data reports logs
if [ ! -f ".env" ]; then
  cp .env.example .env
  echo "[OK] Created .env"
else
  echo "[OK] .env already exists"
fi

# --- Step 7: Run tests ---
echo ""
echo "[STEP 7/7] Running tests..."
pytest -q --tb=no
echo "[OK] All tests passed"

echo ""
echo "=============================================="
echo " SETUP COMPLETE!"
echo "=============================================="
echo ""
echo "Next steps:"
echo "  1. source .venv/bin/activate"
echo "  2. python -m app.main search --query \"AI\" --depth 1 --pages 3"
echo "  3. python -m app.main serve"
echo "  4. Open: http://localhost:8000/docs"
echo ""
echo "Full guide: docs/BEGINNER_PLAYBOOK.md"
echo "=============================================="
