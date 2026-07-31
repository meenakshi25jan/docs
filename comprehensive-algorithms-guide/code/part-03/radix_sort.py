"""Radix sort for Part 3, Chapter 22."""

from __future__ import annotations

from collections.abc import MutableSequence


def radix_sort(items: MutableSequence[int]) -> MutableSequence[int]:
    """Sort non-negative integers in place using LSD radix sort (base 10).

    Time complexity: O(d * (n + k)) where d is digit count, k is radix (10).
    Space complexity: O(n + k) for counting buckets.

    Args:
        items: Mutable sequence of non-negative integers.

    Returns:
        The same sequence, sorted ascending.

    Raises:
        ValueError: If any element is negative.
    """
    if not items:
        return items
    if any(value < 0 for value in items):
        raise ValueError("radix_sort supports non-negative integers only")

    max_value = max(items)
    exp = 1
    while max_value // exp > 0:
        _counting_sort_by_digit(items, exp)
        exp *= 10
    return items


def _counting_sort_by_digit(items: list[int], exp: int) -> None:
    n = len(items)
    output = [0] * n
    count = [0] * 10
    for value in items:
        index = (value // exp) % 10
        count[index] += 1
    for i in range(1, 10):
        count[i] += count[i - 1]
    for i in range(n - 1, -1, -1):
        digit = (items[i] // exp) % 10
        count[digit] -= 1
        output[count[digit]] = items[i]
    items[:] = output


if __name__ == "__main__":
    data = [170, 45, 75, 90, 802, 24, 2, 66]
    print("sorted:", radix_sort(data))
