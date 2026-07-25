"""Chapter 80 — Branch and bound for 0/1 knapsack."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Item:
    weight: int
    value: int


def bound(i: int, w: int, v: int, items: list[Item], capacity: int) -> float:
    if w > capacity:
        return -1.0
    total = v
    wt = w
    for j in range(i, len(items)):
        if wt + items[j].weight <= capacity:
            wt += items[j].weight
            total += items[j].value
        else:
            remaining = capacity - wt
            total += items[j].value * remaining / items[j].weight
            break
    return float(total)


def branch_and_bound(items: list[Item], capacity: int) -> tuple[int, int]:
    items = sorted(items, key=lambda it: it.value / it.weight, reverse=True)
    best_value = 0
    best_weight = 0

    def dfs(i: int, w: int, v: int) -> None:
        nonlocal best_value, best_weight
        if i == len(items):
            if v > best_value:
                best_value, best_weight = v, w
            return
        if bound(i, w, v, items, capacity) < best_value:
            return
        dfs(i + 1, w, v)
        if w + items[i].weight <= capacity:
            dfs(i + 1, w + items[i].weight, v + items[i].value)

    dfs(0, 0, 0)
    return best_value, best_weight


def main() -> float:
    items = [Item(2, 3), Item(3, 4), Item(4, 5), Item(5, 8)]
    value, weight = branch_and_bound(items, capacity=8)
    print(f"Best value: {value}, weight used: {weight}")
    print("SUCCESS: Branch and bound completed")
    return float(value)


if __name__ == "__main__":
    main()
