#!/usr/bin/env python3
"""Vectors, matrices, and linear algebra utilities for Chapter 3."""

from __future__ import annotations

import math
from typing import Sequence


Vector = list[float]
Matrix = list[list[float]]


def dot_product(a: Sequence[float], b: Sequence[float]) -> float:
    """
    Compute the dot product of two vectors.

    Args:
        a: First vector.
        b: Second vector.

    Returns:
        Scalar dot product.

    Raises:
        ValueError: If vectors have different lengths.
    """
    if len(a) != len(b):
        raise ValueError("vectors must have the same length")
    return sum(x * y for x, y in zip(a, b))


def vector_norm(v: Sequence[float]) -> float:
    """
    Compute the Euclidean (L2) norm of a vector.

    Args:
        v: Input vector.

    Returns:
        Non-negative norm length.
    """
    return math.sqrt(sum(x * x for x in v))


def matrix_vector_multiply(matrix: Matrix, vector: Vector) -> Vector:
    """
    Multiply a matrix by a column vector.

    Args:
        matrix: m x n matrix as list of rows.
        vector: Length-n vector.

    Returns:
        Length-m result vector.

    Raises:
        ValueError: On dimension mismatch.
    """
    if not matrix:
        raise ValueError("matrix must not be empty")
    cols: int = len(matrix[0])
    if any(len(row) != cols for row in matrix):
        raise ValueError("matrix rows must have equal length")
    if len(vector) != cols:
        raise ValueError("vector length must match matrix columns")
    return [dot_product(row, vector) for row in matrix]


def cosine_similarity(a: Sequence[float], b: Sequence[float]) -> float:
    """
    Compute cosine similarity between two vectors.

    Args:
        a: First vector.
        b: Second vector.

    Returns:
        Similarity in [-1, 1], or 0.0 if either vector has zero norm.

    Raises:
        ValueError: If vectors have different lengths.
    """
    if len(a) != len(b):
        raise ValueError("vectors must have the same length")
    norm_a = vector_norm(a)
    norm_b = vector_norm(b)
    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0
    return dot_product(a, b) / (norm_a * norm_b)


def transpose(matrix: Matrix) -> Matrix:
    """
    Transpose a matrix.

    Args:
        matrix: Input matrix.

    Returns:
        Transposed matrix.

    Raises:
        ValueError: If matrix is empty or ragged.
    """
    if not matrix:
        raise ValueError("matrix must not be empty")
    cols: int = len(matrix[0])
    if any(len(row) != cols for row in matrix):
        raise ValueError("matrix rows must have equal length")
    return [[matrix[r][c] for r in range(len(matrix))] for c in range(cols)]


def main() -> None:
    """Demonstrate vector and matrix operations."""
    u: Vector = [1.0, 2.0, 3.0]
    v: Vector = [4.0, 5.0, 6.0]
    print(f"u = {u}")
    print(f"v = {v}")
    print(f"dot(u, v) = {dot_product(u, v)}")
    print(f"||u|| = {vector_norm(u):.4f}")
    print(f"cosine_similarity(u, v) = {cosine_similarity(u, v):.6f}")

    matrix: Matrix = [[1.0, 2.0], [3.0, 4.0]]
    vec: Vector = [1.0, 0.0]
    result = matrix_vector_multiply(matrix, vec)
    print(f"\nMatrix:\n  {matrix[0]}\n  {matrix[1]}")
    print(f"Times vector {vec} = {result}")

    t = transpose(matrix)
    print(f"\nTranspose:\n  {t[0]}\n  {t[1]}")


if __name__ == "__main__":
    main()
