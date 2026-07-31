"""Quick sort for Part 3, Chapter 20."""

from __future__ import annotations

import random
from collections.abc import MutableSequence
from typing import TypeVar

T = TypeVar("T")


def quick_sort(items: MutableSequence[T]) -> MutableSequence[T]:
    """Sort *items* in place using quicksort with Lomuto partition.

    Time complexity: O(n log n) average; O(n^2) worst case.
    Space complexity: O(log n) average for recursion stack.

    Args:
        items: Mutable sequence to sort ascending.

    Returns:
        The same sequence, sorted in place.
    """
    _quick_sort_range(items, 0, len(items) - 1)
    return items


def quick_sort_randomized(items: MutableSequence[T]) -> MutableSequence[T]:
    """Quicksort with random pivot to reduce worst-case probability."""
    _quick_sort_randomized_range(items, 0, len(items) - 1)
    return items


def _quick_sort_range(items: MutableSequence[T], low: int, high: int) -> None:
    if low >= high:
        return
    pivot_index = _partition(items, low, high)
    _quick_sort_range(items, low, pivot_index - 1)
    _quick_sort_range(items, pivot_index + 1, high)


def _quick_sort_randomized_range(items: MutableSequence[T], low: int, high: int) -> None:
    if low >= high:
        return
    pivot_choice = random.randint(low, high)
    items[pivot_choice], items[high] = items[high], items[pivot_choice]
    pivot_index = _partition(items, low, high)
    _quick_sort_randomized_range(items, low, pivot_index - 1)
    _quick_sort_randomized_range(items, pivot_index + 1, high)


def _partition(items: MutableSequence[T], low: int, high: int) -> int:
    pivot = items[high]
    i = low
    for j in range(low, high):
        if items[j] <= pivot:
            items[i], items[j] = items[j], items[i]
            i += 1
    items[i], items[high] = items[high], items[i]
    return i


if __name__ == "__main__":
    data = [10, 7, 8, 9, 1, 5]
    print("sorted:", quick_sort(data))
