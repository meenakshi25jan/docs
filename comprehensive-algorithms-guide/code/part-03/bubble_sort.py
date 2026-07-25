"""Bubble sort for Part 3, Chapter 16."""

from __future__ import annotations

from collections.abc import MutableSequence
from typing import TypeVar

T = TypeVar("T")


def bubble_sort(items: MutableSequence[T]) -> MutableSequence[T]:
    """Sort *items* in place using bubble sort.

    Time complexity: O(n^2) worst/average; O(n) best when already sorted.
    Space complexity: O(1).

    Args:
        items: Mutable sequence to sort ascending.

    Returns:
        The same sequence, sorted in place.
    """
    n = len(items)
    for i in range(n):
        swapped = False
        for j in range(0, n - i - 1):
            if items[j] > items[j + 1]:
                items[j], items[j + 1] = items[j + 1], items[j]
                swapped = True
        if not swapped:
            break
    return items


if __name__ == "__main__":
    data = [64, 34, 25, 12, 22, 11, 90]
    print("sorted:", bubble_sort(data))
