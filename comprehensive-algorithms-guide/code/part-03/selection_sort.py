"""Selection sort for Part 3, Chapter 17."""

from __future__ import annotations

from collections.abc import MutableSequence
from typing import TypeVar

T = TypeVar("T")


def selection_sort(items: MutableSequence[T]) -> MutableSequence[T]:
    """Sort *items* in place using selection sort.

    Time complexity: O(n^2) in all cases.
    Space complexity: O(1).

    Args:
        items: Mutable sequence to sort ascending.

    Returns:
        The same sequence, sorted in place.
    """
    n = len(items)
    for i in range(n - 1):
        min_index = i
        for j in range(i + 1, n):
            if items[j] < items[min_index]:
                min_index = j
        if min_index != i:
            items[i], items[min_index] = items[min_index], items[i]
    return items


if __name__ == "__main__":
    data = [29, 10, 14, 37, 13]
    print("sorted:", selection_sort(data))
