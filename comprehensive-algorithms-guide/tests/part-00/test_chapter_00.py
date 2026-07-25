"""Tests for Part 0 — Getting Started code examples."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

CODE_DIR: Path = Path(__file__).resolve().parents[2] / "code" / "part-00"


def test_first_successful_run_exits_zero() -> None:
    """first_successful_run.py should complete without error."""
    result = subprocess.run(
        [sys.executable, str(CODE_DIR / "first_successful_run.py")],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0
    assert "SUCCESS" in result.stdout


def test_sum_squares_small_values() -> None:
    """Verify sum_squares logic via direct import."""
    from measure_execution_time import sum_squares

    assert sum_squares(0) == 0
    assert sum_squares(1) == 1
    assert sum_squares(5) == 55  # 1+4+9+16+25


def test_sum_squares_rejects_negative() -> None:
    """sum_squares should raise on negative input."""
    from measure_execution_time import sum_squares

    with pytest.raises(ValueError, match="non-negative"):
        sum_squares(-1)


def test_measure_execution_time_runs() -> None:
    """measure_execution_time.py should produce timing output."""
    result = subprocess.run(
        [sys.executable, str(CODE_DIR / "measure_execution_time.py")],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0
    assert "Elapsed time" in result.stdout
