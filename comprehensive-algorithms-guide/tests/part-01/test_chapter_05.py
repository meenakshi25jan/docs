"""Tests for Chapter 5 — What Is an Algorithm?"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

from what_is_algorithm import euclidean_gcd, linear_search, verify_algorithm

CODE_DIR: Path = Path(__file__).resolve().parents[2] / "code" / "part-01"


def test_what_is_algorithm_script_runs() -> None:
    """what_is_algorithm.py should exit cleanly."""
    result = subprocess.run(
        [sys.executable, str(CODE_DIR / "what_is_algorithm.py")],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0
    assert "linear_search" in result.stdout


def test_linear_search_found() -> None:
    """Find existing element."""
    assert linear_search([1, 2, 3], 2) == 1


def test_linear_search_missing() -> None:
    """Return -1 when absent."""
    assert linear_search([1, 2, 3], 9) == -1


def test_euclidean_gcd() -> None:
    """Classic GCD example."""
    assert euclidean_gcd(48, 18) == 6


def test_euclidean_gcd_negative() -> None:
    """Negative inputs raise."""
    with pytest.raises(ValueError):
        euclidean_gcd(-1, 5)


def test_verify_algorithm() -> None:
    """All-pass returns empty failure list."""
    failures = verify_algorithm(lambda x: x * 2, {1: 2, 2: 4})
    assert failures == []
