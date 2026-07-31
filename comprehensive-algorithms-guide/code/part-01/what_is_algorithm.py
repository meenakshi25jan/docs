#!/usr/bin/env python3
"""Algorithm fundamentals: correctness and termination for Chapter 5."""

from __future__ import annotations

from typing import Callable, Iterable, TypeVar

T = TypeVar("T")


def linear_search(items: Iterable[T], target: T) -> int:
    """
    Find the index of target in items, or -1 if absent.

    Args:
        items: Sequence to search.
        target: Value to locate.

    Returns:
        Zero-based index of first match, or -1.
    """
    for index, item in enumerate(items):
        if item == target:
            return index
    return -1


def euclidean_gcd(a: int, b: int) -> int:
    """
    Compute greatest common divisor using the Euclidean algorithm.

    Args:
        a: Non-negative integer.
        b: Non-negative integer.

    Returns:
        GCD of a and b.

    Raises:
        ValueError: If either argument is negative.
    """
    if a < 0 or b < 0:
        raise ValueError("arguments must be non-negative")
    while b:
        a, b = b, a % b
    return a


def verify_algorithm(
    fn: Callable[[int], int],
    test_cases: dict[int, int],
) -> list[str]:
    """
    Run a deterministic algorithm against expected outputs.

    Args:
        fn: Function mapping input to output.
        test_cases: Mapping of input -> expected output.

    Returns:
        List of failure messages (empty if all pass).
    """
    failures: list[str] = []
    for inp, expected in test_cases.items():
        actual = fn(inp)
        if actual != expected:
            failures.append(f"input={inp}: expected {expected}, got {actual}")
    return failures


def main() -> None:
    """Demonstrate algorithm properties with search and GCD."""
    data = [10, 20, 30, 40, 50]
    target = 30
    idx = linear_search(data, target)
    print(f"linear_search({data}, {target}) -> index {idx}")

    print(f"\nGCD examples:")
    for a, b in [(48, 18), (101, 10), (0, 7)]:
        print(f"  gcd({a}, {b}) = {euclidean_gcd(a, b)}")

    factorial_cases = {0: 1, 1: 1, 5: 120}

    def factorial(n: int) -> int:
        result = 1
        for i in range(2, n + 1):
            result *= i
        return result

    failures = verify_algorithm(factorial, factorial_cases)
    print(f"\nFactorial verification failures: {failures or 'none'}")


if __name__ == "__main__":
    main()
