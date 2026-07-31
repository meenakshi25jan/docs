# AI English Teacher — Backend setup (Windows PowerShell)
# Usage:
#   .\setup.ps1              # create venv, install deps, copy .env, run migrations
#   .\setup.ps1 -RunTests    # setup + run pytest
#   .\setup.ps1 -StartServer # setup + start uvicorn

param(
    [switch]$RunTests,
    [switch]$StartServer,
    [string]$Python = "python"
)

$ErrorActionPreference = "Stop"
$Root = $PSScriptRoot
Set-Location $Root

function Write-Step([string]$Message) {
    Write-Host "`n==> $Message" -ForegroundColor Cyan
}

Write-Step "Checking Python"
& $Python --version
if ($LASTEXITCODE -ne 0) {
    throw "Python not found. Install Python 3.12+ and ensure '$Python' is on PATH."
}

$venvPython = Join-Path $Root ".venv\Scripts\python.exe"
$venvPip = Join-Path $Root ".venv\Scripts\pip.exe"
$venvAlembic = Join-Path $Root ".venv\Scripts\alembic.exe"
$venvPytest = Join-Path $Root ".venv\Scripts\pytest.exe"
$venvUvicorn = Join-Path $Root ".venv\Scripts\uvicorn.exe"

if (-not (Test-Path $venvPython)) {
    Write-Step "Creating virtual environment"
    & $Python -m venv .venv
    if ($LASTEXITCODE -ne 0) {
        throw "Failed to create virtual environment."
    }
}

Write-Step "Installing dependencies"
& $venvPip install -r requirements.txt
if ($LASTEXITCODE -ne 0) {
    throw "pip install failed."
}

$envFile = Join-Path $Root ".env"
$envExample = Join-Path $Root ".env.example"
if (-not (Test-Path $envFile)) {
    Write-Step "Creating .env from .env.example"
    Copy-Item $envExample $envFile
    Write-Host "Edit .env and set JWT_SECRET before production use." -ForegroundColor Yellow
}

Write-Step "Running database migrations"
& $venvAlembic upgrade head
if ($LASTEXITCODE -ne 0) {
    throw "alembic upgrade head failed."
}

if ($RunTests) {
    Write-Step "Running tests"
    & $venvPytest -v
    if ($LASTEXITCODE -ne 0) {
        throw "pytest failed."
    }
}

if ($StartServer) {
    Write-Step "Starting API server at http://127.0.0.1:8000"
    Write-Host "Press Ctrl+C to stop." -ForegroundColor Yellow
    & $venvUvicorn app.main:app --reload --host 127.0.0.1 --port 8000
    exit $LASTEXITCODE
}

Write-Host "`nSetup complete." -ForegroundColor Green
Write-Host @"

Next steps:
  1. Activate venv:  .\.venv\Scripts\Activate.ps1
  2. Start server:   uvicorn app.main:app --reload
  3. Run tests:      pytest
  4. Health check:   curl http://127.0.0.1:8000/health/live

Or run everything in one go:
  .\setup.ps1 -StartServer
  .\setup.ps1 -RunTests

"@
