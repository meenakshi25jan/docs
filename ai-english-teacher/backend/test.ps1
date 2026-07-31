# AI English Teacher — Run tests (Windows PowerShell)
# Usage:
#   .\test.ps1

$ErrorActionPreference = "Stop"
$Root = $PSScriptRoot
Set-Location $Root

$venvPytest = Join-Path $Root ".venv\Scripts\pytest.exe"

if (-not (Test-Path $venvPytest)) {
    Write-Host "Virtual environment not found. Run .\setup.ps1 first." -ForegroundColor Red
    exit 1
}

& $venvPytest -v
exit $LASTEXITCODE
