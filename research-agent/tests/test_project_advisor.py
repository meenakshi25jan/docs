"""Tests for the universal project advisor."""

import json
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
ADVISOR = PROJECT_ROOT / "scripts" / "project-advisor.py"


def test_advisor_runs_successfully():
    result = subprocess.run(
        [sys.executable, str(ADVISOR), "--project-type", "general"],
        capture_output=True,
        text=True,
        cwd=PROJECT_ROOT,
    )
    assert result.returncode == 0
    assert "UNIVERSAL PROJECT ADVISOR" in result.stdout
    assert "YOUR SYSTEM" in result.stdout


def test_advisor_json_output():
    result = subprocess.run(
        [sys.executable, str(ADVISOR), "--project-type", "web", "--json"],
        capture_output=True,
        text=True,
        cwd=PROJECT_ROOT,
    )
    assert result.returncode == 0
    data = json.loads(result.stdout)
    assert data["project_type"] == "web"
    assert "os" in data
    assert "recommended_stack" in data
    assert "setup_steps" in data
    assert data["os"]["system"] in ("Windows", "Linux", "Darwin")


def test_advisor_lists_project_types():
    result = subprocess.run(
        [sys.executable, str(ADVISOR), "--list-types"],
        capture_output=True,
        text=True,
        cwd=PROJECT_ROOT,
    )
    assert result.returncode == 0
    assert "web" in result.stdout
    assert "ai" in result.stdout
    assert "mobile" in result.stdout


def test_advisor_detects_installed_python():
    result = subprocess.run(
        [sys.executable, str(ADVISOR), "--json"],
        capture_output=True,
        text=True,
        cwd=PROJECT_ROOT,
    )
    data = json.loads(result.stdout)
    installed_names = [t["name"] for t in data["installed_tools"]]
    assert "Python" in installed_names
