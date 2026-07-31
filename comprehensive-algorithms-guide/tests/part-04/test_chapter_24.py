"""Tests for Chapter 24."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

CODE_DIR = Path(__file__).resolve().parents[2] / "code" / "part-04"
SCRIPT = "chapter_24_prims.py"


def test_chapter_24_script_runs() -> None:
    result = subprocess.run(
        [sys.executable, str(CODE_DIR / SCRIPT)],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    assert "=" * 60 in result.stdout
