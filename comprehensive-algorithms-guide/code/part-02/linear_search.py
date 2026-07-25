"""Linear search implementations for Part 2, Chapter 9."""

from __future__ import annotations

from collections.abc import Sequence
from typing import TypeVar

T = TypeVar("T")


def linear_search(items: Sequence[T], target: T) -> int:
    """Return the index of *target* in *items*, or -1 if not found.

    Time complexity: O(n) — each element may be examined once.
    Space complexity: O(1) — only a loop index is stored.

    Args:
        items: Sequence to search (list, tuple, etc.).
        target: Value to locate.

    Returns:
        Zero-based index of the first matching element, or -1.
    """
    for index, value in enumerate(items):
        if value == target:
            return index
    return -1


def linear_search_all(items: Sequence[T], target: T) -> list[int]:
    """Return all indices where *target* appears in *items*.

    Time complexity: O(n).
    Space complexity: O(k) where k is the number of matches.
    """
    return [index for index, value in enumerate(items) if value == target]


def linear_search_with_predicate(items: Sequence[T], predicate) -> int:
    """Return the index of the first item satisfying *predicate*, or -1.

    Time complexity: O(n).
    Space complexity: O(1).
    """
    for index, value in enumerate(items):
        if predicate(value):
            return index
    return -1


if __name__ == "__main__":
    data = [4, 2, 7, 2, 9]
    print("linear_search(7):", linear_search(data, 7))
    print("linear_search(2) all:", linear_search_all(data, 2))
    print("first even:", linear_search_with_predicate(data, lambda x: x % 2 == 0))
