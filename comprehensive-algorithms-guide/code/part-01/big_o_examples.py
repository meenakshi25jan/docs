#!/usr/bin/env python3
"""Big-O complexity examples for Chapter 7."""

from __future__ import annotations

import time
from typing import Callable


def constant_time_lookup(data: dict[int, str], key: int) -> str | None:
    """O(1) average-case dictionary lookup."""
    return data.get(key)


def linear_scan(items: list[int], target: int) -> bool:
    """O(n) linear search."""
    for item in items:
        if item == target:
            return True
    return False


def bubble_sort(arr: list[int]) -> list[int]:
    """O(n^2) bubble sort (educational, not production)."""
    result = arr.copy()
    n = len(result)
    for i in range(n):
        for j in range(0, n - i - 1):
            if result[j] > result[j + 1]:
                result[j], result[j + 1] = result[j + 1], result[j]
    return result


def binary_search(sorted_items: list[int], target: int) -> int:
    """
    O(log n) binary search on a sorted list.

    Returns:
        Index of target, or -1 if not found.
    """
    lo, hi = 0, len(sorted_items) - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        if sorted_items[mid] == target:
            return mid
        if sorted_items[mid] < target:
            lo = mid + 1
        else:
            hi = mid - 1
    return -1


def time_function(fn: Callable[[], object], label: str) -> float:
    """Time a zero-argument callable and print the result."""
    start = time.perf_counter()
    fn()
    elapsed = time.perf_counter() - start
    print(f"{label}: {elapsed:.6f}s")
    return elapsed


def main() -> None:
    """Demonstrate complexity classes with timed examples."""
    lookup_table = {i: f"val_{i}" for i in range(100_000)}
    time_function(lambda: constant_time_lookup(lookup_table, 99_999), "O(1) dict lookup")

    big_list = list(range(100_000))
    time_function(lambda: linear_scan(big_list, 99_999), "O(n) linear scan")

    sorted_list = list(range(100_000))
    time_function(lambda: binary_search(sorted_list, 99_999), "O(log n) binary search")

    small = list(range(500))
    time_function(lambda: bubble_sort(small), "O(n^2) bubble sort n=500")


if __name__ == "__main__":
    main()
