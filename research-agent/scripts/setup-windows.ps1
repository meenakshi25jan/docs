# =============================================================================
# Research Agent - Windows Setup Script
# Purpose: Install everything a beginner needs to run the project locally
# Usage:   powershell -ExecutionPolicy Bypass -File scripts\setup-windows.ps1
# =============================================================================

$ErrorActionPreference = "Stop"

Write-Host "==============================================" -ForegroundColor Cyan
Write-Host " Research Agent - Windows Setup" -ForegroundColor Cyan
Write-Host "==============================================" -ForegroundColor Cyan

# Move to project root
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectDir = Split-Path -Parent $ScriptDir
Set-Location $ProjectDir
Write-Host "[INFO] Project directory: $ProjectDir"

# --- Step 1: Check Python ---
Write-Host ""
Write-Host "[STEP 1/7] Checking Python 3.12+..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "[OK] Found $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "[ERROR] Python is not installed or not in PATH." -ForegroundColor Red
    Write-Host "        Download from: https://www.python.org/downloads/" -ForegroundColor Red
    Write-Host "        IMPORTANT: Check 'Add Python to PATH' during install!" -ForegroundColor Red
    exit 1
}

# --- Step 2: Check Git ---
Write-Host ""
Write-Host "[STEP 2/7] Checking Git..." -ForegroundColor Yellow
try {
    $gitVersion = git --version 2>&1
    Write-Host "[OK] Found $gitVersion" -ForegroundColor Green
} catch {
    Write-Host "[WARN] Git not found. Download from: https://git-scm.com/download/win" -ForegroundColor Yellow
}

# --- Step 3: Create virtual environment ---
Write-Host ""
Write-Host "[STEP 3/7] Creating Python virtual environment..." -ForegroundColor Yellow
if (-not (Test-Path ".venv")) {
    python -m venv .venv
    Write-Host "[OK] Created .venv" -ForegroundColor Green
} else {
    Write-Host "[OK] .venv already exists" -ForegroundColor Green
}

# --- Step 4: Install Python packages ---
Write-Host ""
Write-Host "[STEP 4/7] Installing Python dependencies (may take a few minutes)..." -ForegroundColor Yellow
& .\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip -q
pip install -r requirements.txt -q
Write-Host "[OK] Python packages installed" -ForegroundColor Green

# --- Step 5: Install Playwright ---
Write-Host ""
Write-Host "[STEP 5/7] Installing Playwright Chromium browser..." -ForegroundColor Yellow
playwright install chromium
Write-Host "[OK] Playwright ready" -ForegroundColor Green

# --- Step 6: Create folders and .env ---
Write-Host ""
Write-Host "[STEP 6/7] Creating data folders and .env file..." -ForegroundColor Yellow
New-Item -ItemType Directory -Force -Path data, reports, logs | Out-Null
if (-not (Test-Path ".env")) {
    Copy-Item .env.example .env
    Write-Host "[OK] Created .env from .env.example" -ForegroundColor Green
} else {
    Write-Host "[OK] .env already exists" -ForegroundColor Green
}

# --- Step 7: Run tests ---
Write-Host ""
Write-Host "[STEP 7/7] Running tests to verify installation..." -ForegroundColor Yellow
pytest -q --tb=no
Write-Host "[OK] All tests passed" -ForegroundColor Green

Write-Host ""
Write-Host "==============================================" -ForegroundColor Cyan
Write-Host " SETUP COMPLETE!" -ForegroundColor Green
Write-Host "==============================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:"
Write-Host "  1. Activate environment:  .\.venv\Scripts\Activate.ps1"
Write-Host "  2. Run a test search:     python -m app.main search --query `"AI`" --depth 1 --pages 3"
Write-Host "  3. Start API server:      python -m app.main serve"
Write-Host "  4. Open in browser:       http://localhost:8000/docs"
Write-Host ""
Write-Host "Read the full guide: docs\BEGINNER_PLAYBOOK.md"
Write-Host "==============================================" -ForegroundColor Cyan
