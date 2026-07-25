"""Shared graph types for Part 2 searching algorithms."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Hashable, TypeVar

Node = TypeVar("Node", bound=Hashable)


@dataclass
class WeightedEdge:
    """Directed weighted edge in a graph."""

    source: Hashable
    target: Hashable
    weight: float


@dataclass
class Graph:
    """Adjacency-list graph supporting directed and undirected edges."""

    directed: bool = False
    adjacency: dict[Hashable, list[tuple[Hashable, float]]] = field(default_factory=dict)

    def add_node(self, node: Hashable) -> None:
        """Ensure a node exists in the adjacency map."""
        self.adjacency.setdefault(node, [])

    def add_edge(self, source: Hashable, target: Hashable, weight: float = 1.0) -> None:
        """Add an edge; for undirected graphs, add the reverse edge too."""
        self.add_node(source)
        self.add_node(target)
        self.adjacency[source].append((target, weight))
        if not self.directed:
            self.adjacency[target].append((source, weight))

    def neighbors(self, node: Hashable) -> list[tuple[Hashable, float]]:
        """Return weighted neighbors of a node."""
        return self.adjacency.get(node, [])

    def nodes(self) -> list[Hashable]:
        """Return all nodes in the graph."""
        return list(self.adjacency.keys())
