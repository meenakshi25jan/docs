# =============================================================================
# CREATE PROJECT - Windows
# One command to create and set up the entire Research Agent project.
#
# Usage:
#   powershell -ExecutionPolicy Bypass -File scripts\create-project.ps1
# =============================================================================

$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "╔══════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║         RESEARCH AGENT - CREATE PROJECT                  ║" -ForegroundColor Cyan
Write-Host "║         Setting up everything for you...                 ║" -ForegroundColor Cyan
Write-Host "╚══════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectDir = Split-Path -Parent $ScriptDir
Set-Location $ProjectDir

# Step 1: Detect OS
Write-Host "[1/6] Detected OS: Windows" -ForegroundColor Yellow

# Step 2: Check Python
Write-Host "[2/6] Checking Python..." -ForegroundColor Yellow
try {
    $pyVer = python --version 2>&1
    Write-Host "       Found: $pyVer" -ForegroundColor Green
} catch {
    Write-Host ""
    Write-Host "ERROR: Python is not installed." -ForegroundColor Red
    Write-Host "  Fix: https://www.python.org/downloads/" -ForegroundColor Red
    Write-Host "  IMPORTANT: Check 'Add Python to PATH' during install!" -ForegroundColor Red
    exit 1
}

# Step 3: Run full setup
Write-Host "[3/6] Installing dependencies (may take 3-5 minutes)..." -ForegroundColor Yellow
powershell -ExecutionPolicy Bypass -File scripts\setup-windows.ps1

# Step 4: OS advisor
Write-Host ""
Write-Host "[4/6] Running OS advisor..." -ForegroundColor Yellow
powershell -ExecutionPolicy Bypass -File scripts\advise.ps1 -ProjectType ai

# Step 5: Verify structure
Write-Host ""
Write-Host "[5/6] Verifying project structure..." -ForegroundColor Yellow
@("data", "reports", "logs") | ForEach-Object {
    New-Item -ItemType Directory -Force -Path $_ | Out-Null
    Write-Host "       ✓ $_/" -ForegroundColor Green
}
if (Test-Path ".env") { Write-Host "       ✓ .env" -ForegroundColor Green }
if (Test-Path ".venv") { Write-Host "       ✓ .venv/" -ForegroundColor Green }

# Step 6: Done
Write-Host ""
Write-Host "[6/6] Project created successfully!" -ForegroundColor Green
Write-Host ""
Write-Host "╔══════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║  PROJECT READY! Run these commands:                      ║" -ForegroundColor Cyan
Write-Host "╠══════════════════════════════════════════════════════════╣" -ForegroundColor Cyan
Write-Host "║                                                          ║" -ForegroundColor White
Write-Host "║  .\.venv\Scripts\Activate.ps1                            ║" -ForegroundColor White
Write-Host "║                                                          ║" -ForegroundColor White
Write-Host "║  # Your first research:                                  ║" -ForegroundColor White
Write-Host "║  python -m app.main search `                             ║" -ForegroundColor White
Write-Host "║    --query `"Artificial Intelligence`" `                  ║" -ForegroundColor White
Write-Host "║    --depth 1 --pages 3                                   ║" -ForegroundColor White
Write-Host "║                                                          ║" -ForegroundColor White
Write-Host "║  # Start web interface:                                  ║" -ForegroundColor White
Write-Host "║  python -m app.main serve                                ║" -ForegroundColor White
Write-Host "║  # Then open: http://localhost:8000/docs                 ║" -ForegroundColor White
Write-Host "║                                                          ║" -ForegroundColor White
Write-Host "╚══════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""
Write-Host "Full guide: docs\CREATE_PROJECT.md"
Write-Host ""
