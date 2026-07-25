"""Project 02 — Sorting benchmark tool."""

from __future__ import annotations

import random
import time
from typing import Callable

RNG = random.Random(42)


def bubble_sort(arr: list[int]) -> list[int]:
    a = arr.copy()
    n = len(a)
    for i in range(n):
        for j in range(n - i - 1):
            if a[j] > a[j + 1]:
                a[j], a[j + 1] = a[j + 1], a[j]
    return a


def insertion_sort(arr: list[int]) -> list[int]:
    a = arr.copy()
    for i in range(1, len(a)):
        key = a[i]
        j = i - 1
        while j >= 0 and a[j] > key:
            a[j + 1] = a[j]
            j -= 1
        a[j + 1] = key
    return a


def merge_sort(arr: list[int]) -> list[int]:
    if len(arr) <= 1:
        return arr.copy()

    def merge(left: list[int], right: list[int]) -> list[int]:
        out: list[int] = []
        i = j = 0
        while i < len(left) and j < len(right):
            if left[i] <= right[j]:
                out.append(left[i])
                i += 1
            else:
                out.append(right[j])
                j += 1
        out.extend(left[i:])
        out.extend(right[j:])
        return out

    mid = len(arr) // 2
    return merge(merge_sort(arr[:mid]), merge_sort(arr[mid:]))


def quick_sort(arr: list[int]) -> list[int]:
    if len(arr) <= 1:
        return arr.copy()
    pivot = arr[len(arr) // 2]
    left = [x for x in arr if x < pivot]
    mid = [x for x in arr if x == pivot]
    right = [x for x in arr if x > pivot]
    return quick_sort(left) + mid + quick_sort(right)


def benchmark(name: str, fn: Callable[[list[int]], list[int]], data: list[int]) -> float:
    t0 = time.perf_counter()
    result = fn(data)
    elapsed = time.perf_counter() - t0
    assert result == sorted(data), f"{name} failed correctness"
    return elapsed


def run_benchmarks(sizes: list[int] | None = None) -> dict[str, dict[int, float]]:
    sizes = sizes or [100, 500, 1000]
    algorithms = {
        "bubble": bubble_sort,
        "insertion": insertion_sort,
        "merge": merge_sort,
        "quick": quick_sort,
    }
    results: dict[str, dict[int, float]] = {k: {} for k in algorithms}
    for size in sizes:
        data = [RNG.randint(0, 10_000) for _ in range(size)]
        for name, fn in algorithms.items():
            if name == "bubble" and size > 500:
                continue
            results[name][size] = benchmark(name, fn, data)
    return results


def main() -> int:
    results = run_benchmarks([100, 500])
    total = 0
    for algo, timings in results.items():
        for size, elapsed in timings.items():
            print(f"{algo:10s} n={size:4d}  {elapsed*1000:8.2f} ms")
            total += 1
    print("SUCCESS: Sorting benchmark completed")
    return total


if __name__ == "__main__":
    main()
