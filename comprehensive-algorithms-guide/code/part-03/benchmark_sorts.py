"""Sorting algorithm comparison benchmark for Part 3."""

from __future__ import annotations

import random
import time
from collections.abc import Callable, MutableSequence
from typing import TypeVar

from bubble_sort import bubble_sort
from heap_sort import heap_sort
from insertion_sort import insertion_sort
from merge_sort import merge_sort
from quick_sort import quick_sort_randomized
from radix_sort import radix_sort
from selection_sort import selection_sort
from sorting_utils import is_sorted

T = TypeVar("T")


def _time_sort(
    sort_fn: Callable[[MutableSequence[T]], MutableSequence[T]],
    data: list[T],
) -> float:
    """Return elapsed seconds for one sort run."""
    start = time.perf_counter()
    result = sort_fn(data)
    elapsed = time.perf_counter() - start
    if not is_sorted(result):
        raise RuntimeError(f"{sort_fn.__name__} failed to sort input")
    return elapsed


def benchmark_sorts(
    sizes: list[int] | None = None,
    seed: int = 42,
) -> list[dict[str, float | int | str]]:
    """Benchmark sorting algorithms across input sizes.

    Args:
        sizes: List of input lengths to test. Defaults to [100, 500, 1000].
        seed: Random seed for reproducibility.

    Returns:
        List of result records with algorithm, size, and elapsed seconds.
    """
    if sizes is None:
        sizes = [100, 500, 1000]

    algorithms: list[tuple[str, Callable]] = [
        ("bubble_sort", bubble_sort),
        ("selection_sort", selection_sort),
        ("insertion_sort", insertion_sort),
        ("merge_sort", lambda arr: merge_sort(list(arr))),
        ("quick_sort", quick_sort_randomized),
        ("heap_sort", heap_sort),
        ("radix_sort", radix_sort),
    ]

    results: list[dict[str, float | int | str]] = []
    rng = random.Random(seed)

    for size in sizes:
        base = [rng.randint(0, 10_000) for _ in range(size)]
        for name, sort_fn in algorithms:
            data = list(base)
            elapsed = _time_sort(sort_fn, data)
            results.append({"algorithm": name, "size": size, "seconds": elapsed})

    return results


def print_benchmark_table(results: list[dict[str, float | int | str]]) -> None:
    """Print benchmark results as a formatted table."""
    print(f"{'Algorithm':<18} {'Size':>8} {'Seconds':>12}")
    print("-" * 40)
    for row in results:
        print(f"{row['algorithm']:<18} {row['size']:>8} {row['seconds']:>12.6f}")


if __name__ == "__main__":
    rows = benchmark_sorts([100, 500, 1000])
    print_benchmark_table(rows)
