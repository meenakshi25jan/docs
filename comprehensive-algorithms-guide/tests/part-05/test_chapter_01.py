"""Tests for Chapter 1 — Functions, Sets, and Logic."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

from sets_logic import (
    evaluate_proposition,
    is_injective,
    power_set,
    set_operations,
)

CODE_DIR: Path = Path(__file__).resolve().parents[2] / "code" / "part-05"


def test_sets_logic_script_runs() -> None:
    """sets_logic.py should exit cleanly."""
    result = subprocess.run(
        [sys.executable, str(CODE_DIR / "sets_logic.py")],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0
    assert "union" in result.stdout


def test_is_injective() -> None:
    """Double is injective on small integers; modulo is not."""
    assert is_injective(lambda x: x * 2, range(5))
    assert not is_injective(lambda x: x % 2, range(5))


def test_power_set_size() -> None:
    """Power set of n elements has 2^n subsets."""
    subsets = power_set(["a", "b", "c"])
    assert len(subsets) == 8


def test_set_operations() -> None:
    """Union and intersection behave correctly."""
    a, b = {1, 2, 3}, {3, 4, 5}
    ops = set_operations(a, b)
    assert ops["union"] == {1, 2, 3, 4, 5}
    assert ops["intersection"] == {3}


def test_evaluate_proposition_invalid() -> None:
    """Unknown operator raises ValueError."""
    with pytest.raises(ValueError, match="Unknown operator"):
        evaluate_proposition(True, False, "nand")
