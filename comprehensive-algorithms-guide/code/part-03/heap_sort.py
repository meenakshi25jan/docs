"""Heap sort for Part 3, Chapter 21."""

from __future__ import annotations

from collections.abc import MutableSequence
from typing import TypeVar

T = TypeVar("T")


def heap_sort(items: MutableSequence[T]) -> MutableSequence[T]:
    """Sort *items* in place using heap sort.

    Time complexity: O(n log n) in all cases.
    Space complexity: O(1) excluding recursion stack O(log n).

    Args:
        items: Mutable sequence to sort ascending.

    Returns:
        The same sequence, sorted in place.
    """
    n = len(items)
    for start in range(n // 2 - 1, -1, -1):
        _heapify(items, n, start)
    for end in range(n - 1, 0, -1):
        items[0], items[end] = items[end], items[0]
        _heapify(items, end, 0)
    return items


def _heapify(items: MutableSequence[T], heap_size: int, root: int) -> None:
    largest = root
    left = 2 * root + 1
    right = 2 * root + 2
    if left < heap_size and items[left] > items[largest]:
        largest = left
    if right < heap_size and items[right] > items[largest]:
        largest = right
    if largest != root:
        items[root], items[largest] = items[largest], items[root]
        _heapify(items, heap_size, largest)


if __name__ == "__main__":
    data = [12, 11, 13, 5, 6, 7]
    print("sorted:", heap_sort(data))
