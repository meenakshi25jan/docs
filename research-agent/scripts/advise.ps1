# =============================================================================
# Universal Project Advisor - Windows launcher
# Detects your OS and prints tailored setup suggestions for ANY project.
#
# Usage:
#   powershell -File scripts\advise.ps1
#   powershell -File scripts\advise.ps1 -ProjectType web
#   powershell -File scripts\advise.ps1 -ProjectType ai -Json
# =============================================================================

param(
    [string]$ProjectType = "general",
    [switch]$Json,
    [switch]$ListTypes
)

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectDir = Split-Path -Parent $ScriptDir
Set-Location $ProjectDir

# Use venv Python if available
if (Test-Path ".\.venv\Scripts\python.exe") {
    $Python = ".\.venv\Scripts\python.exe"
} else {
    $Python = "python"
}

Write-Host "[INFO] Running Project Advisor for: $ProjectType" -ForegroundColor Cyan
Write-Host "[INFO] Python: $Python" -ForegroundColor Cyan
Write-Host ""

$args_list = @("scripts/project-advisor.py", "--project-type", $ProjectType)
if ($Json) { $args_list += "--json" }
if ($ListTypes) { $args_list += "--list-types" }

& $Python @args_list
