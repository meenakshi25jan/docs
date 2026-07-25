"""Tests for Chapter 73."""

from __future__ import annotations

import importlib
import subprocess
import sys
from pathlib import Path

CODE_DIR = Path(__file__).resolve().parents[2] / "code" / "part-10"
MODULE = "ch73_sgd"


def test_script_success() -> None:
    result = subprocess.run(
        [sys.executable, str(CODE_DIR / f"{MODULE}.py")],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    assert "SUCCESS" in result.stdout


def test_core_behavior() -> None:
    mod = importlib.import_module(MODULE)
    result = mod.main()
    assert result < 0.5
