# setup-and-run.ps1
#
# One script to: create backend/.env if missing (prompting for the values
# that must be real), install backend + frontend dependencies, and start
# both servers.
#
# Usage: place at project ROOT (same level as backend/ and frontend/), then:
#   .\setup-and-run.ps1
#
# Re-running later just starts the servers (it skips setup steps that are
# already done).

$ErrorActionPreference = "Stop"

$root = $PSScriptRoot
$backendPath = Join-Path $root "backend"
$frontendPath = Join-Path $root "frontend"
$envPath = Join-Path $backendPath ".env"
$envExamplePath = Join-Path $backendPath ".env.example"
$venvPath = Join-Path $backendPath ".venv"

if (-not (Test-Path $backendPath)) { Write-Error "Backend folder not found at: $backendPath"; exit 1 }
if (-not (Test-Path $frontendPath)) { Write-Error "Frontend folder not found at: $frontendPath"; exit 1 }

# ---------------------------------------------------------------------------
# 1. Create backend/.env if it doesn't exist yet
# ---------------------------------------------------------------------------
if (-not (Test-Path $envPath)) {
    Write-Host "No backend/.env found - let's create one." -ForegroundColor Cyan
    Write-Host ""

    $databaseUrl = Read-Host "Neon DATABASE_URL (postgresql+asyncpg://user:pass@host/db?ssl=require)"
    while ([string]::IsNullOrWhiteSpace($databaseUrl)) {
        $databaseUrl = Read-Host "DATABASE_URL can't be empty - paste your Neon connection string"
    }

    $grokApiBase = Read-Host "LLM API base URL [default: https://api.groq.com/openai/v1]"
    if ([string]::IsNullOrWhiteSpace($grokApiBase)) { $grokApiBase = "https://api.groq.com/openai/v1" }

    $grokApiKey = Read-Host "LLM API key (Groq/xAI/etc)"
    while ([string]::IsNullOrWhiteSpace($grokApiKey)) {
        $grokApiKey = Read-Host "API key can't be empty - paste your key"
    }

    $grokModel = Read-Host "LLM model name [default: openai/gpt-oss-120b]"
    if ([string]::IsNullOrWhiteSpace($grokModel)) { $grokModel = "openai/gpt-oss-120b" }

    $frontendOrigin = Read-Host "Frontend dev URL [default: http://localhost:5173]"
    if ([string]::IsNullOrWhiteSpace($frontendOrigin)) { $frontendOrigin = "http://localhost:5173" }

    # generate a random JWT secret rather than asking the user to invent one
    $bytes = New-Object byte[] 32
    [System.Security.Cryptography.RandomNumberGenerator]::Create().GetBytes($bytes)
    $jwtSecret = [System.BitConverter]::ToString($bytes) -replace "-", ""

    $envContent = @"
# Neon Postgres connection string (asyncpg-compatible form)
DATABASE_URL=$databaseUrl

# LLM API (variable names kept as GROK_* regardless of actual provider)
GROK_API_KEY=$grokApiKey
GROK_API_BASE=$grokApiBase
GROK_MODEL=$grokModel

# Auth
JWT_SECRET=$jwtSecret
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=1440

# CORS - your frontend dev URL
FRONTEND_ORIGIN=$frontendOrigin
"@

    Set-Content -Path $envPath -Value $envContent -Encoding UTF8
    Write-Host "Created backend\.env" -ForegroundColor Green
    Write-Host ""
} else {
    Write-Host "backend\.env already exists - skipping setup." -ForegroundColor DarkGray
}

# ---------------------------------------------------------------------------
# 2. Backend: create venv (if missing) and install dependencies
# ---------------------------------------------------------------------------
if (-not (Test-Path $venvPath)) {
    Write-Host "Creating Python virtual environment..." -ForegroundColor Cyan
    python -m venv $venvPath
}

$venvPython = Join-Path $venvPath "Scripts\python.exe"
$venvActivate = Join-Path $venvPath "Scripts\Activate.ps1"

Write-Host "Installing backend dependencies..." -ForegroundColor Cyan
& $venvPython -m pip install --upgrade pip --quiet
& $venvPython -m pip install -r (Join-Path $backendPath "requirements.txt") --quiet

# ---------------------------------------------------------------------------
# 3. Frontend: install npm dependencies if node_modules is missing
# ---------------------------------------------------------------------------
$nodeModulesPath = Join-Path $frontendPath "node_modules"
if (-not (Test-Path $nodeModulesPath)) {
    Write-Host "Installing frontend dependencies (npm install)..." -ForegroundColor Cyan
    Push-Location $frontendPath
    npm install
    Pop-Location
} else {
    Write-Host "Frontend node_modules already installed - skipping." -ForegroundColor DarkGray
}

# ---------------------------------------------------------------------------
# 4. Reminder: pgvector must be enabled once on Neon (can't be done from here)
# ---------------------------------------------------------------------------
Write-Host ""
Write-Host "Reminder: if you haven't already, run this once in your Neon SQL editor:" -ForegroundColor Yellow
Write-Host "  CREATE EXTENSION IF NOT EXISTS vector;" -ForegroundColor Yellow
Write-Host ""

# ---------------------------------------------------------------------------
# 5. Start backend + frontend in separate windows
# ---------------------------------------------------------------------------
Write-Host "Starting backend..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList @(
    "-NoExit",
    "-Command",
    "cd `"$backendPath`"; & `"$venvActivate`"; python -m uvicorn app.main:app --reload --port 8000"
)

Start-Sleep -Seconds 2

Write-Host "Starting frontend..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList @(
    "-NoExit",
    "-Command",
    "cd `"$frontendPath`"; npm run dev"
)

Write-Host ""
Write-Host "Backend:  http://127.0.0.1:8000" -ForegroundColor Green
Write-Host "Frontend: check its terminal window for the local URL (usually http://localhost:5173)" -ForegroundColor Green
Write-Host ""
Write-Host "Two new PowerShell windows were opened - one per service. Close them to stop." -ForegroundColor Yellow
