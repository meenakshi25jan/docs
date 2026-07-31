"""Tests for Chapter 3 — Vectors, Matrices, and Linear Algebra."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

from linear_algebra_basics import (
    cosine_similarity,
    dot_product,
    matrix_vector_multiply,
    transpose,
    vector_norm,
)

CODE_DIR: Path = Path(__file__).resolve().parents[2] / "code" / "part-05"


def test_linear_algebra_script_runs() -> None:
    """linear_algebra_basics.py should exit cleanly."""
    result = subprocess.run(
        [sys.executable, str(CODE_DIR / "linear_algebra_basics.py")],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0
    assert "dot" in result.stdout.lower()


def test_dot_product() -> None:
    """Standard dot product."""
    assert dot_product([1, 2], [3, 4]) == 11


def test_vector_norm() -> None:
    """Unit vector has norm 1."""
    assert vector_norm([1.0, 0.0]) == pytest.approx(1.0)


def test_matrix_vector_multiply() -> None:
    """Identity-like multiplication."""
    m = [[1.0, 0.0], [0.0, 1.0]]
    assert matrix_vector_multiply(m, [3.0, 4.0]) == [3.0, 4.0]


def test_cosine_similarity_identical() -> None:
    """Identical vectors have similarity 1."""
    v = [1.0, 2.0, 3.0]
    assert cosine_similarity(v, v) == pytest.approx(1.0)


def test_transpose() -> None:
    """Transpose swaps rows and columns."""
    m = [[1, 2], [3, 4]]
    assert transpose(m) == [[1, 3], [2, 4]]
