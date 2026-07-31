#!/usr/bin/env python3
"""Chapter 25 — Kruskal's algorithm for minimum spanning tree."""

from __future__ import annotations

from graph_utils import Graph, build_sample_graph


class UnionFind:
    """Disjoint-set union with path compression and union by rank."""

    def __init__(self, items: list[str]) -> None:
        self.parent = {item: item for item in items}
        self.rank = {item: 0 for item in items}

    def find(self, item: str) -> str:
        if self.parent[item] != item:
            self.parent[item] = self.find(self.parent[item])
        return self.parent[item]

    def union(self, a: str, b: str) -> bool:
        """Union sets containing a and b. Returns False if already connected."""
        root_a, root_b = self.find(a), self.find(b)
        if root_a == root_b:
            return False
        if self.rank[root_a] < self.rank[root_b]:
            root_a, root_b = root_b, root_a
        self.parent[root_b] = root_a
        if self.rank[root_a] == self.rank[root_b]:
            self.rank[root_a] += 1
        return True


def kruskals_mst(graph: Graph) -> tuple[list[tuple[str, str, float]], float]:
    """Compute MST using Kruskal's algorithm."""
    vertices = graph.vertices()
    edges = sorted(graph.edge_list(), key=lambda edge: edge[2])
    uf = UnionFind(vertices)
    mst: list[tuple[str, str, float]] = []
    total = 0.0

    for u, v, weight in edges:
        if uf.union(u, v):
            mst.append((u, v, weight))
            total += weight
        if len(mst) == len(vertices) - 1:
            break

    if len(mst) != len(vertices) - 1:
        raise ValueError("Graph is disconnected; MST does not span all vertices")

    return mst, total


def main() -> None:
    """Run Kruskal's algorithm on the sample graph."""
    graph = build_sample_graph()
    mst_edges, total = kruskals_mst(graph)

    print("=" * 60)
    print("Chapter 25 — Kruskal's Minimum Spanning Tree")
    print("=" * 60)
    print("MST edges (u, v, weight):")
    for u, v, w in mst_edges:
        print(f"  {u} — {v}  weight={w}")
    print(f"\nTotal MST weight: {total}")
    print("=" * 60)


if __name__ == "__main__":
    main()
