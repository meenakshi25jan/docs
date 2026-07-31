"""Merge sort for Part 3, Chapter 19."""

from __future__ import annotations

from collections.abc import MutableSequence, Sequence
from typing import TypeVar

T = TypeVar("T")


def merge_sort(items: MutableSequence[T]) -> MutableSequence[T]:
    """Sort *items* using merge sort (returns new sorted list).

    Time complexity: O(n log n) in all cases.
    Space complexity: O(n) for auxiliary arrays.

    Args:
        items: Sequence to sort ascending.

    Returns:
        New sorted list.
    """
    if len(items) <= 1:
        return list(items)
    mid = len(items) // 2
    left = merge_sort(items[:mid])
    right = merge_sort(items[mid:])
    return _merge(left, right)


def merge_sort_in_place(items: MutableSequence[T]) -> MutableSequence[T]:
    """In-place merge sort variant using auxiliary buffer."""
    buffer = list(items)
    _merge_sort_inplace(items, buffer, 0, len(items))
    return items


def _merge_sort_inplace(
    items: MutableSequence[T],
    buffer: list[T],
    start: int,
    end: int,
) -> None:
    if end - start <= 1:
        return
    mid = start + (end - start) // 2
    _merge_sort_inplace(items, buffer, start, mid)
    _merge_sort_inplace(items, buffer, mid, end)
    buffer[start:end] = items[start:end]
    i, j, k = start, mid, start
    while i < mid and j < end:
        if buffer[i] <= buffer[j]:
            items[k] = buffer[i]
            i += 1
        else:
            items[k] = buffer[j]
            j += 1
        k += 1
    while i < mid:
        items[k] = buffer[i]
        i += 1
        k += 1
    while j < end:
        items[k] = buffer[j]
        j += 1
        k += 1


def _merge(left: Sequence[T], right: Sequence[T]) -> list[T]:
    result: list[T] = []
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


if __name__ == "__main__":
    data = [38, 27, 43, 3, 9, 82, 10]
    print("sorted:", merge_sort(data))
