"""A* search algorithm for Part 2, Chapter 15."""

from __future__ import annotations

import heapq
import math
from collections.abc import Callable
from typing import Hashable

from graph_types import Graph


Heuristic = Callable[[Hashable, Hashable], float]


def manhattan_heuristic(a: tuple[int, int], b: tuple[int, int]) -> float:
    """Manhattan distance for grid coordinates."""
    return float(abs(a[0] - b[0]) + abs(a[1] - b[1]))


def a_star(
    graph: Graph,
    start: Hashable,
    goal: Hashable,
    heuristic: Heuristic,
) -> tuple[list[Hashable] | None, float]:
    """Find lowest-cost path using A* with admissible heuristic.

    Time complexity: depends on heuristic quality; worst case similar to Dijkstra.
    Space complexity: O(V).

    Args:
        graph: Weighted graph with non-negative edges.
        start: Start node.
        goal: Goal node.
        heuristic: Function h(node, goal) estimating remaining cost.

    Returns:
        (path, total_cost) or (None, inf) if no path exists.
    """
    open_set: list[tuple[float, float, Hashable]] = []
    heapq.heappush(open_set, (heuristic(start, goal), 0.0, start))

    g_score: dict[Hashable, float] = {start: 0.0}
    came_from: dict[Hashable, Hashable] = {}
    closed: set[Hashable] = set()

    while open_set:
        _, current_g, current = heapq.heappop(open_set)
        if current in closed:
            continue
        if current == goal:
            return _reconstruct(came_from, current), current_g
        closed.add(current)

        for neighbor, weight in graph.neighbors(current):
            if weight < 0:
                raise ValueError("A* requires non-negative edge weights")
            tentative_g = current_g + weight
            if tentative_g >= g_score.get(neighbor, math.inf):
                continue
            came_from[neighbor] = current
            g_score[neighbor] = tentative_g
            f_score = tentative_g + heuristic(neighbor, goal)
            heapq.heappush(open_set, (f_score, tentative_g, neighbor))

    return None, math.inf


def _reconstruct(came_from: dict[Hashable, Hashable], current: Hashable) -> list[Hashable]:
    path = [current]
    while current in came_from:
        current = came_from[current]
        path.append(current)
    path.reverse()
    return path


if __name__ == "__main__":
    grid = Graph(directed=False)
    nodes = [(x, y) for x in range(3) for y in range(3)]
    for node in nodes:
        grid.add_node(node)
    for x in range(3):
        for y in range(3):
            if x + 1 < 3:
                grid.add_edge((x, y), (x + 1, y), 1.0)
            if y + 1 < 3:
                grid.add_edge((x, y), (x, y + 1), 1.0)
    path, cost = a_star(grid, (0, 0), (2, 2), manhattan_heuristic)
    print("path:", path)
    print("cost:", cost)
