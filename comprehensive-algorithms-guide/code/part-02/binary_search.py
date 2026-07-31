"""Binary search implementations for Part 2, Chapter 10."""

from __future__ import annotations

from collections.abc import Sequence
from typing import TypeVar

T = TypeVar("T")


def binary_search_iterative(items: Sequence[T], target: T) -> int:
    """Iterative binary search on a sorted sequence.

    Time complexity: O(log n).
    Space complexity: O(1).

    Args:
        items: Sorted sequence in ascending order.
        target: Value to find.

    Returns:
        Index of *target*, or -1 if absent.
    """
    left, right = 0, len(items) - 1
    while left <= right:
        mid = left + (right - left) // 2
        if items[mid] == target:
            return mid
        if items[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    return -1


def binary_search_recursive(
    items: Sequence[T],
    target: T,
    left: int = 0,
    right: int | None = None,
) -> int:
    """Recursive binary search on a sorted sequence.

    Time complexity: O(log n).
    Space complexity: O(log n) due to call stack.
    """
    if right is None:
        right = len(items) - 1
    if left > right:
        return -1
    mid = left + (right - left) // 2
    if items[mid] == target:
        return mid
    if items[mid] < target:
        return binary_search_recursive(items, target, mid + 1, right)
    return binary_search_recursive(items, target, left, mid - 1)


def lower_bound(items: Sequence[T], target: T) -> int:
    """Return the leftmost index where *target* could be inserted.

    Time complexity: O(log n).
    Space complexity: O(1).
    """
    left, right = 0, len(items)
    while left < right:
        mid = left + (right - left) // 2
        if items[mid] < target:
            left = mid + 1
        else:
            right = mid
    return left


if __name__ == "__main__":
    sorted_data = [1, 3, 5, 7, 9, 11]
    print("iterative:", binary_search_iterative(sorted_data, 7))
    print("recursive:", binary_search_recursive(sorted_data, 4))
    print("lower_bound(5):", lower_bound(sorted_data, 5))
