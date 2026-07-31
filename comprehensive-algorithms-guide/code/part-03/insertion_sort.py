"""Insertion sort for Part 3, Chapter 18."""

from __future__ import annotations

from collections.abc import MutableSequence
from typing import TypeVar

T = TypeVar("T")


def insertion_sort(items: MutableSequence[T]) -> MutableSequence[T]:
    """Sort *items* in place using insertion sort.

    Time complexity: O(n^2) worst/average; O(n) best when nearly sorted.
    Space complexity: O(1).

    Args:
        items: Mutable sequence to sort ascending.

    Returns:
        The same sequence, sorted in place.
    """
    for i in range(1, len(items)):
        key = items[i]
        j = i - 1
        while j >= 0 and items[j] > key:
            items[j + 1] = items[j]
            j -= 1
        items[j + 1] = key
    return items


if __name__ == "__main__":
    data = [5, 2, 4, 6, 1, 3]
    print("sorted:", insertion_sort(data))
