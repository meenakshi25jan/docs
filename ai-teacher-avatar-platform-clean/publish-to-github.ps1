# publish-to-github.ps1
#
# Replaces the ENTIRE contents and history of the GitHub repo below with the
# cleaned project in this folder, as a single fresh commit. This permanently
# removes the old commits that contained real credentials from the branch.
#
# BEFORE RUNNING — rotate the leaked credentials (the old ones are public):
#   1. Neon: console.neon.tech -> your project -> Roles -> reset password for neondb_owner
#   2. Groq: console.groq.com -> API Keys -> revoke the old key, create a new one
#
# Usage (PowerShell, from this folder):  .\publish-to-github.ps1

$ErrorActionPreference = "Stop"

$RepoUrl = "https://github.com/meenakshi25jan/ai-teacher-avatar-platform.git"
$Source  = $PSScriptRoot

$confirm = Read-Host "This will OVERWRITE all history of $RepoUrl. Have you rotated the Neon password and Groq API key? (yes/no)"
if ($confirm -ne "yes") { Write-Host "Aborted."; exit 1 }

# Stage the publishable files in a temp dir (everything except this script and any .git)
$staging = Join-Path ([System.IO.Path]::GetTempPath()) ("publish-" + [Guid]::NewGuid().ToString("N"))
New-Item -ItemType Directory -Path $staging | Out-Null
robocopy $Source $staging /E /XF "publish-to-github.ps1" /XD ".git" ".venv" "venv" "node_modules" "__pycache__" | Out-Null
if ($LASTEXITCODE -ge 8) { Write-Error "robocopy failed"; exit 1 }

Push-Location $staging
git init -b main
git add -A
git commit -m "Clean repository: AI Voice English Teacher (secrets removed, single project)"
git remote add origin $RepoUrl
git push --force origin main
Pop-Location

Remove-Item -Recurse -Force $staging
Write-Host ""
Write-Host "Done. Check https://github.com/meenakshi25jan/ai-teacher-avatar-platform" -ForegroundColor Green
Write-Host "Note: GitHub can cache old commits for a while even after a force-push;" -ForegroundColor Yellow
Write-Host "rotating the credentials (step above) is what actually makes the leak harmless." -ForegroundColor Yellow
