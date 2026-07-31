# AI English Teacher — Start API server (Windows PowerShell)
# Usage:
#   .\run.ps1

$ErrorActionPreference = "Stop"
$Root = $PSScriptRoot
Set-Location $Root

$venvPython = Join-Path $Root ".venv\Scripts\python.exe"
$venvUvicorn = Join-Path $Root ".venv\Scripts\uvicorn.exe"

if (-not (Test-Path $venvPython)) {
    Write-Host "Virtual environment not found. Run .\setup.ps1 first." -ForegroundColor Red
    exit 1
}

if (-not (Test-Path (Join-Path $Root ".env"))) {
    Write-Host ".env not found. Run .\setup.ps1 first." -ForegroundColor Red
    exit 1
}

Write-Host "Starting API at http://127.0.0.1:8000" -ForegroundColor Cyan
Write-Host "Docs: http://127.0.0.1:8000/docs" -ForegroundColor Cyan
Write-Host "Press Ctrl+C to stop.`n" -ForegroundColor Yellow

& $venvUvicorn app.main:app --reload --host 127.0.0.1 --port 8000
