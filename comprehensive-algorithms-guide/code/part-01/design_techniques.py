#!/usr/bin/env python3
"""Algorithm design techniques for Chapter 8."""

from __future__ import annotations

from functools import lru_cache
from typing import Any


def factorial_recursive(n: int) -> int:
    """
    Compute n! using divide-and-conquer recursion.

    Args:
        n: Non-negative integer.

    Returns:
        n factorial.

    Raises:
        ValueError: If n is negative.
    """
    if n < 0:
        raise ValueError("n must be non-negative")
    if n <= 1:
        return 1
    return n * factorial_recursive(n - 1)


@lru_cache(maxsize=None)
def fibonacci_memo(n: int) -> int:
    """
    Compute the nth Fibonacci number with memoization.

    Args:
        n: Non-negative index.

    Returns:
        F(n) where F(0)=0, F(1)=1.

    Raises:
        ValueError: If n is negative.
    """
    if n < 0:
        raise ValueError("n must be non-negative")
    if n < 2:
        return n
    return fibonacci_memo(n - 1) + fibonacci_memo(n - 2)


def merge_sort(arr: list[int]) -> list[int]:
    """
    Sort a list using divide-and-conquer merge sort.

    Args:
        arr: List of integers.

    Returns:
        New sorted list.
    """
    if len(arr) <= 1:
        return arr.copy()
    mid = len(arr) // 2
    left = merge_sort(arr[:mid])
    right = merge_sort(arr[mid:])
    return _merge(left, right)


def _merge(left: list[int], right: list[int]) -> list[int]:
    """Merge two sorted lists."""
    result: list[int] = []
    i = j = 0
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1
    result.extend(left[i:])
    result.extend(right[j:])
    return result


def coin_change_greedy(coins: list[int], amount: int) -> dict[str, Any]:
    """
    Greedy coin change (works for canonical systems like US coins).

    Args:
        coins: Available coin denominations (positive integers).
        amount: Target amount.

    Returns:
        Dictionary with coin counts and remainder.

    Raises:
        ValueError: If amount is negative.
    """
    if amount < 0:
        raise ValueError("amount must be non-negative")
    sorted_coins = sorted(coins, reverse=True)
    remaining = amount
    counts: dict[int, int] = {}
    for coin in sorted_coins:
        if coin <= 0:
            continue
        count, remaining = divmod(remaining, coin)
        if count:
            counts[coin] = count
    return {"coins": counts, "remainder": remaining}


def main() -> None:
    """Demonstrate recursion, memoization, divide-and-conquer, and greedy."""
    print(f"factorial(6) = {factorial_recursive(6)}")
    print(f"fibonacci_memo(30) = {fibonacci_memo(30)}")
    print(f"merge_sort([3,1,4,1,5,9,2,6]) = {merge_sort([3, 1, 4, 1, 5, 9, 2, 6])}")
    change = coin_change_greedy([25, 10, 5, 1], 67)
    print(f"coin_change_greedy(67 cents): {change}")


if __name__ == "__main__":
    main()
