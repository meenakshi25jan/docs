"""Depth-first search for Part 2, Chapter 11."""

from __future__ import annotations

from collections.abc import Callable, Hashable, Iterable
from typing import TypeVar

from graph_types import Graph

Node = TypeVar("Node", bound=Hashable)


def dfs_recursive(
    graph: Graph,
    start: Hashable,
    visited: set[Hashable] | None = None,
) -> list[Hashable]:
    """Depth-first traversal using recursion.

    Time complexity: O(V + E).
    Space complexity: O(V) for visited set and recursion stack.
    """
    if visited is None:
        visited = set()
    order: list[Hashable] = []
    if start in visited:
        return order
    visited.add(start)
    order.append(start)
    for neighbor, _ in graph.neighbors(start):
        order.extend(dfs_recursive(graph, neighbor, visited))
    return order


def dfs_iterative(graph: Graph, start: Hashable) -> list[Hashable]:
    """Depth-first traversal using an explicit stack.

    Time complexity: O(V + E).
    Space complexity: O(V).
    """
    visited: set[Hashable] = set()
    order: list[Hashable] = []
    stack: list[Hashable] = [start]
    while stack:
        node = stack.pop()
        if node in visited:
            continue
        visited.add(node)
        order.append(node)
        for neighbor, _ in reversed(graph.neighbors(node)):
            if neighbor not in visited:
                stack.append(neighbor)
    return order


def dfs_path(
    graph: Graph,
    start: Hashable,
    goal: Hashable,
) -> list[Hashable] | None:
    """Find a path from *start* to *goal* using DFS.

    Time complexity: O(V + E) in the worst case.
    Space complexity: O(V).
    """
    stack: list[tuple[Hashable, list[Hashable]]] = [(start, [start])]
    visited: set[Hashable] = set()
    while stack:
        node, path = stack.pop()
        if node in visited:
            continue
        visited.add(node)
        if node == goal:
            return path
        for neighbor, _ in graph.neighbors(node):
            if neighbor not in visited:
                stack.append((neighbor, path + [neighbor]))
    return None


if __name__ == "__main__":
    g = Graph()
    for edge in [("A", "B"), ("A", "C"), ("B", "D"), ("C", "D"), ("D", "E")]:
        g.add_edge(*edge)
    print("recursive:", dfs_recursive(g, "A"))
    print("iterative:", dfs_iterative(g, "A"))
    print("path A->E:", dfs_path(g, "A", "E"))
