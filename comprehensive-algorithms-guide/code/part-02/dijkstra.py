"""Dijkstra's shortest-path algorithm for Part 2, Chapter 13."""

from __future__ import annotations

import heapq
import math
from typing import Hashable

from graph_types import Graph


def dijkstra(
    graph: Graph,
    source: Hashable,
) -> tuple[dict[Hashable, float], dict[Hashable, Hashable | None]]:
    """Compute shortest distances from *source* to all reachable nodes.

    Uses a min-heap priority queue. Non-negative edge weights are required.

    Time complexity: O((V + E) log V) with a binary heap.
    Space complexity: O(V).

    Args:
        graph: Weighted directed or undirected graph.
        source: Starting node.

    Returns:
        Tuple of (distance map, predecessor map for path reconstruction).
    """
    distances: dict[Hashable, float] = {node: math.inf for node in graph.nodes()}
    predecessors: dict[Hashable, Hashable | None] = {node: None for node in graph.nodes()}
    if source not in distances:
        return distances, predecessors

    distances[source] = 0.0
    heap: list[tuple[float, Hashable]] = [(0.0, source)]

    while heap:
        current_dist, node = heapq.heappop(heap)
        if current_dist > distances[node]:
            continue
        for neighbor, weight in graph.neighbors(node):
            if weight < 0:
                raise ValueError("Dijkstra requires non-negative edge weights")
            new_dist = current_dist + weight
            if new_dist < distances[neighbor]:
                distances[neighbor] = new_dist
                predecessors[neighbor] = node
                heapq.heappush(heap, (new_dist, neighbor))

    return distances, predecessors


def reconstruct_path(
    predecessors: dict[Hashable, Hashable | None],
    source: Hashable,
    goal: Hashable,
) -> list[Hashable] | None:
    """Rebuild shortest path from predecessor map produced by Dijkstra."""
    if goal not in predecessors or predecessors[goal] is None and goal != source:
        if goal != source:
            return None
    path: list[Hashable] = []
    current: Hashable | None = goal
    while current is not None:
        path.append(current)
        current = predecessors.get(current)
    path.reverse()
    if path and path[0] == source:
        return path
    return None


if __name__ == "__main__":
    g = Graph(directed=True)
    edges = [
        ("A", "B", 4),
        ("A", "C", 2),
        ("B", "C", 1),
        ("B", "D", 5),
        ("C", "D", 8),
        ("C", "E", 10),
        ("D", "E", 2),
    ]
    for s, t, w in edges:
        g.add_edge(s, t, w)
    dist, pred = dijkstra(g, "A")
    print("distances:", dist)
    print("path A->E:", reconstruct_path(pred, "A", "E"))
