#!/usr/bin/env python3
"""Chapter 27 — Topological sort (Kahn's algorithm and DFS)."""

from __future__ import annotations

from collections import defaultdict, deque


def build_course_graph() -> tuple[dict[str, list[str]], dict[str, int]]:
    """Return adjacency list and in-degree for a DAG example."""
    edges = [
        ("Intro", "LinearAlgebra"),
        ("Intro", "Probability"),
        ("LinearAlgebra", "ML"),
        ("Probability", "ML"),
        ("ML", "DeepLearning"),
        ("ML", "Graphs"),
        ("Graphs", "PageRank"),
    ]
    adjacency: dict[str, list[str]] = defaultdict(list)
    indegree: dict[str, int] = defaultdict(int)
    nodes: set[str] = set()
    for u, v in edges:
        adjacency[u].append(v)
        indegree[v] += 1
        nodes.update([u, v])
    for node in nodes:
        indegree.setdefault(node, 0)
    return adjacency, indegree


def topological_sort_kahn(
    adjacency: dict[str, list[str]], indegree: dict[str, int]
) -> list[str]:
    """Kahn's BFS-based topological sort."""
    queue = deque(sorted(node for node, deg in indegree.items() if deg == 0))
    order: list[str] = []
    degrees = dict(indegree)

    while queue:
        node = queue.popleft()
        order.append(node)
        for neighbor in adjacency[node]:
            degrees[neighbor] -= 1
            if degrees[neighbor] == 0:
                queue.append(neighbor)

    if len(order) != len(degrees):
        raise ValueError("Graph has a cycle; topological sort impossible")
    return order


def topological_sort_dfs(adjacency: dict[str, list[str]], nodes: list[str]) -> list[str]:
    """DFS-based topological sort."""
    visited: set[str] = set()
    stack: list[str] = []
    temp: set[str] = set()

    def dfs(node: str) -> None:
        if node in temp:
            raise ValueError("Graph has a cycle; topological sort impossible")
        if node in visited:
            return
        temp.add(node)
        for neighbor in adjacency[node]:
            dfs(neighbor)
        temp.remove(node)
        visited.add(node)
        stack.append(node)

    for node in sorted(nodes):
        if node not in visited:
            dfs(node)
    return list(reversed(stack))


def main() -> None:
    """Demonstrate topological ordering of course prerequisites."""
    adjacency, indegree = build_course_graph()
    nodes = sorted(indegree.keys())
    kahn_order = topological_sort_kahn(adjacency, indegree)
    dfs_order = topological_sort_dfs(adjacency, nodes)

    print("=" * 60)
    print("Chapter 27 — Topological Sort")
    print("=" * 60)
    print("Kahn (BFS) order:")
    print("  " + " -> ".join(kahn_order))
    print("\nDFS order:")
    print("  " + " -> ".join(dfs_order))
    print("=" * 60)


if __name__ == "__main__":
    main()
