#!/usr/bin/env python3
"""
Measure execution time for a simple algorithm-style loop.

Demonstrates time.perf_counter() for high-resolution timing.
"""

from __future__ import annotations

import time


def sum_squares(n: int) -> int:
    """
    Compute the sum of squares from 1 to n.

    Args:
        n: Upper bound (inclusive). Must be non-negative.

    Returns:
        Sum of i*i for i in 1..n.

    Raises:
        ValueError: If n is negative.
    """
    if n < 0:
        raise ValueError("n must be non-negative")
    total: int = 0
    for i in range(1, n + 1):
        total += i * i
    return total


def main() -> None:
    """Run sum_squares with timing."""
    n: int = 1_000_000
    start: float = time.perf_counter()
    result: int = sum_squares(n)
    elapsed: float = time.perf_counter() - start

    print(f"sum_squares({n:,}) = {result:,}")
    print(f"Elapsed time: {elapsed:.6f} seconds")


if __name__ == "__main__":
    main()
