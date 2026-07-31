"""Shared helpers for Part 3 sorting algorithms."""

from __future__ import annotations

from collections.abc import Callable, MutableSequence
from typing import TypeVar

T = TypeVar("T")

SortFunc = Callable[[MutableSequence[T]], MutableSequence[T]]


def is_sorted(items: MutableSequence[T]) -> bool:
    """Return True if *items* is sorted in non-decreasing order."""
    return all(items[i] <= items[i + 1] for i in range(len(items) - 1))


def copy_list(items: MutableSequence[T]) -> list[T]:
    """Return a shallow copy of *items* as a list."""
    return list(items)
