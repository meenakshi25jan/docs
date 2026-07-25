"""Tests for Chapter 4 — Calculus and Optimization."""

from __future__ import annotations

import math
import subprocess
import sys
from pathlib import Path

import pytest

from calculus_optimization import gradient_descent, newton_method, numerical_derivative

CODE_DIR: Path = Path(__file__).resolve().parents[2] / "code" / "part-05"


def test_calculus_script_runs() -> None:
    """calculus_optimization.py should exit cleanly."""
    result = subprocess.run(
        [sys.executable, str(CODE_DIR / "calculus_optimization.py")],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0
    assert "Gradient descent" in result.stdout


def test_numerical_derivative() -> None:
    """Derivative of x^2 at 3 is approximately 6."""
    deriv = numerical_derivative(lambda x: x * x, 3.0)
    assert deriv == pytest.approx(6.0, rel=1e-4)


def test_gradient_descent_converges() -> None:
    """Minimize (x-2)^2 from x=10."""
    grad = lambda x: 2.0 * (x - 2.0)
    final_x, _ = gradient_descent(grad, x0=10.0, learning_rate=0.3, steps=50)
    assert final_x == pytest.approx(2.0, abs=0.01)


def test_newton_method_sqrt2() -> None:
    """Newton finds sqrt(2) root of x^2 - 2."""
    f = lambda x: x * x - 2.0
    df = lambda x: 2.0 * x
    root = newton_method(f, df, x0=1.0)
    assert root == pytest.approx(math.sqrt(2), rel=1e-8)


def test_numerical_derivative_invalid_h() -> None:
    """Non-positive step size raises."""
    with pytest.raises(ValueError, match="positive"):
        numerical_derivative(lambda x: x, 1.0, h=0.0)
