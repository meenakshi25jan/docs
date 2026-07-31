"""Shared graph utilities for Part 4 — Graph Algorithms."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from typing import DefaultDict, Iterable


@dataclass
class Graph:
    """Weighted undirected graph using adjacency list."""

    adjacency: DefaultDict[str, list[tuple[str, float]]] = field(
        default_factory=lambda: defaultdict(list)
    )
    directed: bool = False

    def add_edge(self, u: str, v: str, weight: float = 1.0) -> None:
        """Add edge (u, v) with optional weight."""
        self.adjacency[u].append((v, weight))
        if not self.directed:
            self.adjacency[v].append((u, weight))

    def vertices(self) -> list[str]:
        """Return sorted vertex labels."""
        nodes: set[str] = set(self.adjacency.keys())
        for neighbors in self.adjacency.values():
            for neighbor, _ in neighbors:
                nodes.add(neighbor)
        return sorted(nodes)

    def edge_list(self) -> list[tuple[str, str, float]]:
        """Return unique undirected edges as (u, v, weight) with u < v."""
        seen: set[tuple[str, str]] = set()
        edges: list[tuple[str, str, float]] = []
        for u, neighbors in self.adjacency.items():
            for v, weight in neighbors:
                key = (u, v) if u < v else (v, u)
                if key not in seen:
                    seen.add(key)
                    edges.append((key[0], key[1], weight))
        return edges


def build_sample_graph() -> Graph:
    """Return a small weighted graph used across MST examples."""
    graph = Graph()
    edges: list[tuple[str, str, float]] = [
        ("A", "B", 4.0),
        ("A", "C", 2.0),
        ("B", "C", 1.0),
        ("B", "D", 5.0),
        ("C", "D", 8.0),
        ("C", "E", 10.0),
        ("D", "E", 2.0),
    ]
    for u, v, w in edges:
        graph.add_edge(u, v, w)
    return graph


def adjacency_matrix(
    vertices: Iterable[str], edges: list[tuple[str, str, float]], inf: float = float("inf")
) -> tuple[list[str], list[list[float]]]:
    """Build adjacency matrix from edge list."""
    labels = sorted(set(vertices))
    index = {label: i for i, label in enumerate(labels)}
    n = len(labels)
    matrix = [[inf if i != j else 0.0 for j in range(n)] for i in range(n)]
    for u, v, w in edges:
        i, j = index[u], index[v]
        matrix[i][j] = min(matrix[i][j], w)
        matrix[j][i] = min(matrix[j][i], w)
    return labels, matrix
