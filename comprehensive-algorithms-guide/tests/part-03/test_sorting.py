"""Tests for Part 3 — Sorting algorithms."""

from __future__ import annotations

import random
import subprocess
import sys
from pathlib import Path

import pytest

from benchmark_sorts import benchmark_sorts
from bubble_sort import bubble_sort
from heap_sort import heap_sort
from insertion_sort import insertion_sort
from merge_sort import merge_sort, merge_sort_in_place
from quick_sort import quick_sort, quick_sort_randomized
from radix_sort import radix_sort
from selection_sort import selection_sort
from sorting_utils import is_sorted

CODE_DIR = Path(__file__).resolve().parents[2] / "code" / "part-03"

SORT_FUNCTIONS = [
    bubble_sort,
    selection_sort,
    insertion_sort,
    lambda arr: merge_sort(list(arr)),
    merge_sort_in_place,
    quick_sort,
    quick_sort_randomized,
    heap_sort,
    radix_sort,
]


@pytest.mark.parametrize("sort_fn", SORT_FUNCTIONS)
def test_sorts_random_input(sort_fn) -> None:
    data = [random.randint(-50, 50) for _ in range(30)]
    if sort_fn is radix_sort:
        data = [abs(x) for x in data]
    sorted_data = list(data)
    result = sort_fn(sorted_data)
    assert is_sorted(result)


@pytest.mark.parametrize("sort_fn", SORT_FUNCTIONS)
def test_sorts_empty_and_single(sort_fn) -> None:
    assert sort_fn([]) == []
    single = [42]
    if sort_fn is radix_sort:
        assert sort_fn(single) == [42]
    else:
        assert sort_fn(single) == [42]


def test_radix_sort_rejects_negative() -> None:
    with pytest.raises(ValueError, match="non-negative"):
        radix_sort([-1, 2, 3])


def test_merge_sort_returns_new_list() -> None:
    original = [3, 1, 2]
    result = merge_sort(original)
    assert result == [1, 2, 3]
    assert original == [3, 1, 2]


def test_benchmark_sorts_runs() -> None:
    results = benchmark_sorts([50, 100], seed=0)
    assert len(results) == 7 * 2
    for row in results:
        assert row["seconds"] >= 0


def test_benchmark_script_exits_zero() -> None:
    result = subprocess.run(
        [sys.executable, str(CODE_DIR / "benchmark_sorts.py")],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0
    assert "bubble_sort" in result.stdout
