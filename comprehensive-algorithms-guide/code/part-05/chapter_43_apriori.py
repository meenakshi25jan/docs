#!/usr/bin/env python3
"""Chapter 43 — Apriori frequent itemset mining."""

from __future__ import annotations

from itertools import combinations
from typing import Iterable


def apriori(
    transactions: list[frozenset[str]],
    min_support: float = 0.3,
) -> list[tuple[frozenset[str], float]]:
    """
    Find frequent itemsets using Apriori algorithm.

    Returns list of (itemset, support) sorted by size then support.
    """
    n = len(transactions)
    if n == 0:
        return []

    def support(itemset: frozenset[str]) -> float:
        count = sum(1 for txn in transactions if itemset.issubset(txn))
        return count / n

    # L1: frequent 1-itemsets
    items: set[str] = set()
    for txn in transactions:
        items.update(txn)

    frequent: list[tuple[frozenset[str], float]] = []
    current = [(frozenset({item}), support(frozenset({item}))) for item in sorted(items)]
    current = [(iset, sup) for iset, sup in current if sup >= min_support]
    k = 1

    while current:
        frequent.extend(current)
        k += 1
        candidates: set[frozenset[str]] = set()
        prev_sets = [iset for iset, _ in current]
        for i in range(len(prev_sets)):
            for j in range(i + 1, len(prev_sets)):
                union = prev_sets[i] | prev_sets[j]
                if len(union) == k:
                    candidates.add(union)

        next_level: list[tuple[frozenset[str], float]] = []
        for candidate in sorted(candidates, key=lambda s: sorted(s)):
            subsets = [frozenset(sub) for sub in combinations(candidate, k - 1)]
            if all(any(f[0] == sub for f in frequent if len(f[0]) == k - 1) for sub in subsets):
                sup = support(candidate)
                if sup >= min_support:
                    next_level.append((candidate, sup))
        current = next_level

    return sorted(frequent, key=lambda x: (len(x[0]), -x[1]))


def transactions_from_lists(rows: Iterable[Iterable[str]]) -> list[frozenset[str]]:
    """Convert iterable of baskets to frozensets."""
    return [frozenset(row) for row in rows]


def main() -> None:
    """Run Apriori on a grocery basket example."""
    baskets = [
        ["milk", "bread", "butter"],
        ["beer", "diapers", "chips"],
        ["milk", "diapers", "beer", "eggs"],
        ["bread", "butter", "milk"],
        ["beer", "chips", "diapers"],
        ["milk", "bread", "diapers"],
        ["butter", "bread"],
        ["beer", "milk", "diapers"],
    ]
    transactions = transactions_from_lists(baskets)
    min_support = 0.3
    frequent = apriori(transactions, min_support=min_support)

    print("=" * 60)
    print("Chapter 43 — Apriori Frequent Itemsets")
    print("Dataset: Synthetic grocery baskets")
    print("=" * 60)
    print(f"Transactions: {len(transactions)}, min_support: {min_support}")
    print("Frequent itemsets:")
    for itemset, sup in frequent:
        items = ", ".join(sorted(itemset))
        print(f"  {{{items}}}  support={sup:.2f}")
    print("=" * 60)


if __name__ == "__main__":
    main()
