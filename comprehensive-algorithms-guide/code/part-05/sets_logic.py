#!/usr/bin/env python3
"""Functions, sets, and logic utilities for Chapter 1."""

from __future__ import annotations

from typing import Callable, Iterable, TypeVar

T = TypeVar("T")


def is_injective(f: Callable[[T], object], domain: Iterable[T]) -> bool:
    """
    Check whether a function is injective (one-to-one) on a finite domain.

    Args:
        f: Function to test.
        domain: Iterable of domain elements.

    Returns:
        True if no two distinct inputs map to the same output.
    """
    seen: set[object] = set()
    for x in domain:
        y = f(x)
        if y in seen:
            return False
        seen.add(y)
    return True


def power_set(items: Iterable[T]) -> list[frozenset[T]]:
    """
    Return the power set of a finite iterable as a list of frozensets.

    Args:
        items: Finite collection of hashable elements.

    Returns:
        List of all subsets, including the empty set.
    """
    elements: list[T] = list(items)
    result: list[frozenset[T]] = []
    n: int = len(elements)
    for mask in range(1 << n):
        subset: set[T] = {elements[i] for i in range(n) if mask & (1 << i)}
        result.append(frozenset(subset))
    return result


def evaluate_proposition(p: bool, q: bool, op: str) -> bool:
    """
    Evaluate a binary logical proposition.

    Args:
        p: First boolean operand.
        q: Second boolean operand.
        op: One of 'and', 'or', 'implies', 'iff', 'xor'.

    Returns:
        Truth value of the proposition.

    Raises:
        ValueError: If op is not recognized.
    """
    if op == "and":
        return p and q
    if op == "or":
        return p or q
    if op == "implies":
        return (not p) or q
    if op == "iff":
        return p == q
    if op == "xor":
        return p != q
    raise ValueError(f"Unknown operator: {op}")


def set_operations(a: set[T], b: set[T]) -> dict[str, set[T]]:
    """
    Compute standard set operations on two sets.

    Args:
        a: First set.
        b: Second set.

    Returns:
        Dictionary with union, intersection, difference, and symmetric difference.
    """
    return {
        "union": a | b,
        "intersection": a & b,
        "difference": a - b,
        "symmetric_difference": a ^ b,
    }


def main() -> None:
    """Demonstrate sets, functions, and logic."""
    evens: set[int] = {2, 4, 6, 8}
    primes: set[int] = {2, 3, 5, 7}
    ops = set_operations(evens, primes)
    print("Set A (evens):", sorted(evens))
    print("Set B (primes):", sorted(primes))
    for name, value in ops.items():
        print(f"  {name}: {sorted(value)}")

    double = lambda x: x * 2
    domain = range(5)
    print(f"\nDouble is injective on {list(domain)}:", is_injective(double, domain))

    p, q = True, False
    print(f"\nLogic: p={p}, q={q}")
    for op in ("and", "or", "implies", "iff", "xor"):
        print(f"  {op}: {evaluate_proposition(p, q, op)}")

    subsets = power_set(["a", "b"])
    print(f"\nPower set of {{a, b}} ({len(subsets)} subsets):")
    for s in sorted(subsets, key=lambda x: (len(x), sorted(x))):
        print(f"  {set(s)}")


if __name__ == "__main__":
    main()
