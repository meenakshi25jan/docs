"""Tests for Chapter 7 — Big-O Complexity."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from big_o_examples import binary_search, bubble_sort, constant_time_lookup, linear_scan

CODE_DIR: Path = Path(__file__).resolve().parents[2] / "code" / "part-01"


def test_big_o_script_runs() -> None:
    """big_o_examples.py should exit cleanly."""
    result = subprocess.run(
        [sys.executable, str(CODE_DIR / "big_o_examples.py")],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0
    assert "O(1)" in result.stdout


def test_constant_time_lookup() -> None:
    """Dictionary lookup returns value."""
    d = {1: "one", 2: "two"}
    assert constant_time_lookup(d, 2) == "two"


def test_linear_scan() -> None:
    """Linear scan finds target."""
    assert linear_scan([1, 2, 3], 2) is True
    assert linear_scan([1, 2, 3], 9) is False


def test_binary_search() -> None:
    """Binary search on sorted list."""
    items = [1, 3, 5, 7, 9]
    assert binary_search(items, 5) == 2
    assert binary_search(items, 4) == -1


def test_bubble_sort() -> None:
    """Bubble sort orders list."""
    assert bubble_sort([3, 1, 2]) == [1, 2, 3]
