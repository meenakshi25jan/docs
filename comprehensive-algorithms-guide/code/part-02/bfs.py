"""Breadth-first search for Part 2, Chapter 12."""

from __future__ import annotations

from collections import deque
from typing import Hashable

from graph_types import Graph


def bfs(graph: Graph, start: Hashable) -> list[Hashable]:
    """Breadth-first traversal order from *start*.

    Time complexity: O(V + E).
    Space complexity: O(V) for queue and visited set.
    """
    visited: set[Hashable] = {start}
    order: list[Hashable] = []
    queue: deque[Hashable] = deque([start])
    while queue:
        node = queue.popleft()
        order.append(node)
        for neighbor, _ in graph.neighbors(node):
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append(neighbor)
    return order


def bfs_shortest_path_unweighted(
    graph: Graph,
    start: Hashable,
    goal: Hashable,
) -> list[Hashable] | None:
    """Shortest path (fewest edges) in an unweighted graph.

    Time complexity: O(V + E).
    Space complexity: O(V).
    """
    if start == goal:
        return [start]
    visited: set[Hashable] = {start}
    queue: deque[tuple[Hashable, list[Hashable]]] = deque([(start, [start])])
    while queue:
        node, path = queue.popleft()
        for neighbor, _ in graph.neighbors(node):
            if neighbor in visited:
                continue
            next_path = path + [neighbor]
            if neighbor == goal:
                return next_path
            visited.add(neighbor)
            queue.append((neighbor, next_path))
    return None


def bfs_levels(graph: Graph, start: Hashable) -> dict[Hashable, int]:
    """Return the BFS depth (hop count) of each reachable node from *start*.

    Time complexity: O(V + E).
    Space complexity: O(V).
    """
    levels: dict[Hashable, int] = {start: 0}
    queue: deque[Hashable] = deque([start])
    while queue:
        node = queue.popleft()
        for neighbor, _ in graph.neighbors(node):
            if neighbor not in levels:
                levels[neighbor] = levels[node] + 1
                queue.append(neighbor)
    return levels


if __name__ == "__main__":
    g = Graph()
    for edge in [("A", "B"), ("A", "C"), ("B", "D"), ("C", "D"), ("D", "E")]:
        g.add_edge(*edge)
    print("bfs:", bfs(g, "A"))
    print("shortest A->E:", bfs_shortest_path_unweighted(g, "A", "E"))
    print("levels:", bfs_levels(g, "A"))
