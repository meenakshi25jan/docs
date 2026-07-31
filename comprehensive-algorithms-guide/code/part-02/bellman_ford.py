"""Bellman-Ford shortest-path algorithm for Part 2, Chapter 14."""

from __future__ import annotations

import math
from typing import Hashable

from graph_types import Graph, WeightedEdge


def bellman_ford(
    graph: Graph,
    source: Hashable,
) -> tuple[dict[Hashable, float], dict[Hashable, Hashable | None], bool]:
    """Compute shortest paths; detect negative-weight cycles.

    Time complexity: O(V * E).
    Space complexity: O(V).

    Args:
        graph: Graph with possibly negative edge weights.
        source: Starting node.

    Returns:
        (distances, predecessors, has_no_negative_cycle)
    """
    nodes = graph.nodes()
    distances: dict[Hashable, float] = {node: math.inf for node in nodes}
    predecessors: dict[Hashable, Hashable | None] = {node: None for node in nodes}
    if source not in distances:
        return distances, predecessors, True

    distances[source] = 0.0
    edge_list = _collect_edges(graph)

    for _ in range(len(nodes) - 1):
        updated = False
        for edge in edge_list:
            if distances[edge.source] == math.inf:
                continue
            candidate = distances[edge.source] + edge.weight
            if candidate < distances[edge.target]:
                distances[edge.target] = candidate
                predecessors[edge.target] = edge.source
                updated = True
        if not updated:
            break

    for edge in edge_list:
        if distances[edge.source] == math.inf:
            continue
        if distances[edge.source] + edge.weight < distances[edge.target]:
            return distances, predecessors, False

    return distances, predecessors, True


def _collect_edges(graph: Graph) -> list[WeightedEdge]:
    """Flatten adjacency list into edge records."""
    edges: list[WeightedEdge] = []
    seen: set[tuple[Hashable, Hashable]] = set()
    for node in graph.nodes():
        for neighbor, weight in graph.neighbors(node):
            key = (node, neighbor)
            if key in seen:
                continue
            seen.add(key)
            edges.append(WeightedEdge(node, neighbor, weight))
    return edges


if __name__ == "__main__":
    g = Graph(directed=True)
    for s, t, w in [("A", "B", 6), ("A", "C", 7), ("B", "C", 8), ("C", "B", -3)]:
        g.add_edge(s, t, w)
    dist, pred, ok = bellman_ford(g, "A")
    print("distances:", dist)
    print("no negative cycle:", ok)
