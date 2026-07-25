#!/usr/bin/env python3
"""Chapter 28 — PageRank algorithm."""

from __future__ import annotations

from collections import defaultdict

import networkx as nx


def build_web_graph() -> dict[str, list[str]]:
    """Small directed web graph for PageRank demonstration."""
    return {
        "A": ["B", "C"],
        "B": ["C"],
        "C": ["A"],
        "D": ["C"],
    }


def pagerank(
    graph: dict[str, list[str]],
    damping: float = 0.85,
    max_iter: int = 100,
    tol: float = 1e-6,
) -> dict[str, float]:
    """Compute PageRank using power iteration."""
    nodes = sorted(graph.keys())
    outlinks: dict[str, list[str]] = {n: graph.get(n, []) for n in nodes}
    n = len(nodes)
    rank = {node: 1.0 / n for node in nodes}
    teleport = (1.0 - damping) / n

    for _ in range(max_iter):
        new_rank: dict[str, float] = {node: teleport for node in nodes}
        for node in nodes:
            targets = outlinks[node]
            if not targets:
                share = damping * rank[node] / n
                for target in nodes:
                    new_rank[target] += share
            else:
                share = damping * rank[node] / len(targets)
                for target in targets:
                    new_rank[target] += share

        delta = sum(abs(new_rank[node] - rank[node]) for node in nodes)
        rank = new_rank
        if delta < tol:
            break

    return rank


def pagerank_networkx(graph: dict[str, list[str]]) -> dict[str, float]:
    """Reference PageRank via NetworkX."""
    g = nx.DiGraph()
    for node, targets in graph.items():
        for target in targets:
            g.add_edge(node, target)
    return nx.pagerank(g, alpha=0.85)


def main() -> None:
    """Run PageRank on a toy web graph."""
    graph = build_web_graph()
    custom = pagerank(graph)
    reference = pagerank_networkx(graph)

    print("=" * 60)
    print("Chapter 28 — PageRank")
    print("=" * 60)
    print("Custom implementation:")
    for node in sorted(custom):
        print(f"  {node}: {custom[node]:.6f}")
    print("\nNetworkX reference:")
    for node in sorted(reference):
        print(f"  {node}: {reference[node]:.6f}")
    print("=" * 60)


if __name__ == "__main__":
    main()
