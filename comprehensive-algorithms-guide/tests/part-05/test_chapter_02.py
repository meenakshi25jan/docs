"""Tests for Chapter 2 — Probability and Statistics."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

from probability_basics import (
    bayes_posterior,
    binomial_pmf,
    empirical_probability,
    mean_and_variance,
    summarize_distribution,
)

CODE_DIR: Path = Path(__file__).resolve().parents[2] / "code" / "part-05"


def test_probability_basics_script_runs() -> None:
    """probability_basics.py should exit cleanly."""
    result = subprocess.run(
        [sys.executable, str(CODE_DIR / "probability_basics.py")],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0
    assert "Bayes" in result.stdout


def test_empirical_probability() -> None:
    """Three heads out of four flips."""
    assert empirical_probability(["H", "H", "T", "H"], "H") == 0.75


def test_bayes_posterior() -> None:
    """Toy spam filter posterior."""
    post = bayes_posterior(0.1, 0.8, 0.15)
    assert 0.0 < post < 1.0


def test_mean_and_variance() -> None:
    """Constant list has zero variance."""
    mu, var = mean_and_variance([5.0, 5.0, 5.0])
    assert mu == 5.0
    assert var == 0.0


def test_binomial_pmf_invalid() -> None:
    """k > n raises ValueError."""
    with pytest.raises(ValueError):
        binomial_pmf(3, 5, 0.5)


def test_summarize_distribution() -> None:
    """Summary includes expected keys."""
    stats = summarize_distribution([1.0, 2.0, 3.0])
    assert "mean" in stats
    assert stats["count"] == 3.0
