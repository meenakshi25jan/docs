#!/usr/bin/env python3
"""Chapter 24 — Prim's algorithm for minimum spanning tree."""

from __future__ import annotations

import heapq

from graph_utils import Graph, build_sample_graph


def prims_mst(graph: Graph, start: str | None = None) -> tuple[list[tuple[str, str, float]], float]:
    """
    Compute MST using Prim's algorithm with a min-heap.

    Returns (mst_edges, total_weight).
    """
    vertices = graph.vertices()
    if not vertices:
        return [], 0.0

    root = start or vertices[0]
    visited: set[str] = {root}
    heap: list[tuple[float, str, str]] = []

    for neighbor, weight in graph.adjacency[root]:
        heapq.heappush(heap, (weight, root, neighbor))

    mst: list[tuple[str, str, float]] = []
    total = 0.0

    while heap and len(visited) < len(vertices):
        weight, u, v = heapq.heappop(heap)
        if v in visited:
            continue
        visited.add(v)
        mst.append((u, v, weight))
        total += weight
        for next_node, next_weight in graph.adjacency[v]:
            if next_node not in visited:
                heapq.heappush(heap, (next_weight, v, next_node))

    if len(visited) != len(vertices):
        raise ValueError("Graph is disconnected; MST does not span all vertices")

    return mst, total


def main() -> None:
    """Run Prim's algorithm on the sample graph."""
    graph = build_sample_graph()
    mst_edges, total = prims_mst(graph, start="A")

    print("=" * 60)
    print("Chapter 24 — Prim's Minimum Spanning Tree")
    print("=" * 60)
    print("MST edges (u, v, weight):")
    for u, v, w in mst_edges:
        print(f"  {u} — {v}  weight={w}")
    print(f"\nTotal MST weight: {total}")
    print("=" * 60)


if __name__ == "__main__":
    main()
