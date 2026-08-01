# AI English Teacher — Backend dev script (Windows PowerShell)
#
# Usage:
#   .\dev.ps1              # setup + start API server (default)
#   .\dev.ps1 -Test        # setup + run tests
#   .\dev.ps1 -SetupOnly   # setup only (no server/tests)
#
# First time on Windows:
#   Set-ExecutionPolicy -Scope CurrentUser RemoteSigned

param(
    [switch]$Test,
    [switch]$SetupOnly,
    [string]$Python = "python",
    [string]$Host = "127.0.0.1",
    [int]$Port = 8000
)

$ErrorActionPreference = "Stop"
$Root = $PSScriptRoot
Set-Location $Root

function Write-Step([string]$Message) {
    Write-Host "`n==> $Message" -ForegroundColor Cyan
}

function Ensure-Setup {
    Write-Step "Checking Python"
    & $Python --version
    if ($LASTEXITCODE -ne 0) {
        throw "Python not found. Install Python 3.12+ and ensure '$Python' is on PATH."
    }

    $script:VenvPython = Join-Path $Root ".venv\Scripts\python.exe"
    $script:VenvPip = Join-Path $Root ".venv\Scripts\pip.exe"
    $script:VenvAlembic = Join-Path $Root ".venv\Scripts\alembic.exe"
    $script:VenvPytest = Join-Path $Root ".venv\Scripts\pytest.exe"
    $script:VenvUvicorn = Join-Path $Root ".venv\Scripts\uvicorn.exe"

    if (-not (Test-Path $script:VenvPython)) {
        Write-Step "Creating virtual environment"
        & $Python -m venv .venv
        if ($LASTEXITCODE -ne 0) {
            throw "Failed to create virtual environment."
        }
    }

    Write-Step "Installing dependencies"
    & $script:VenvPip install -r requirements.txt
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
    & $script:VenvAlembic upgrade head
    if ($LASTEXITCODE -ne 0) {
        throw "alembic upgrade head failed."
    }
}

Ensure-Setup

if ($SetupOnly) {
    Write-Host "`nSetup complete." -ForegroundColor Green
    exit 0
}

if ($Test) {
    Write-Step "Running tests"
    & $VenvPytest -v
    exit $LASTEXITCODE
}

Write-Step "Starting API server at http://${Host}:${Port}"
Write-Host "Docs: http://${Host}:${Port}/docs" -ForegroundColor Green
Write-Host "Health: http://${Host}:${Port}/health/live" -ForegroundColor Green
Write-Host "Press Ctrl+C to stop.`n" -ForegroundColor Yellow

& $VenvUvicorn app.main:app --reload --host $Host --port $Port
exit $LASTEXITCODE
