"""Tests for Chapter 8 — Algorithm Design Techniques."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

from design_techniques import (
    coin_change_greedy,
    factorial_recursive,
    fibonacci_memo,
    merge_sort,
)

CODE_DIR: Path = Path(__file__).resolve().parents[2] / "code" / "part-01"


def test_design_techniques_script_runs() -> None:
    """design_techniques.py should exit cleanly."""
    result = subprocess.run(
        [sys.executable, str(CODE_DIR / "design_techniques.py")],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0
    assert "merge_sort" in result.stdout


def test_factorial() -> None:
    """5! = 120."""
    assert factorial_recursive(5) == 120


def test_fibonacci_memo() -> None:
    """Fibonacci sequence values."""
    assert fibonacci_memo(0) == 0
    assert fibonacci_memo(10) == 55


def test_merge_sort() -> None:
    """Merge sort handles duplicates."""
    assert merge_sort([3, 1, 2, 1]) == [1, 1, 2, 3]


def test_coin_change_greedy() -> None:
    """US coins for 67 cents."""
    result = coin_change_greedy([25, 10, 5, 1], 67)
    assert result["remainder"] == 0
    assert sum(k * v for k, v in result["coins"].items()) == 67


def test_factorial_negative() -> None:
    """Negative factorial raises."""
    with pytest.raises(ValueError):
        factorial_recursive(-1)
