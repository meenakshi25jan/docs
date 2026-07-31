#!/usr/bin/env python3
"""Chapter 23 — Graph Representations (adjacency list, matrix, edge list)."""

from __future__ import annotations

import json
from collections import defaultdict

import networkx as nx

from graph_utils import Graph, adjacency_matrix, build_sample_graph


def edge_list_representation(graph: Graph) -> list[tuple[str, str, float]]:
    """Return edges as a flat list."""
    return graph.edge_list()


def adjacency_list_representation(graph: Graph) -> dict[str, list[tuple[str, float]]]:
    """Return adjacency list as a plain dict."""
    return {node: list(neighbors) for node, neighbors in sorted(graph.adjacency.items())}


def networkx_from_graph(graph: Graph) -> nx.Graph:
    """Convert internal Graph to an undirected NetworkX graph."""
    g = nx.Graph()
    for u, v, w in graph.edge_list():
        g.add_edge(u, v, weight=w)
    return g


def main() -> None:
    """Demonstrate three graph representations."""
    graph = build_sample_graph()
    vertices = graph.vertices()
    edges = edge_list_representation(graph)

    labels, matrix = adjacency_matrix(vertices, edges)
    adj_list = adjacency_list_representation(graph)
    nx_graph = networkx_from_graph(graph)

    print("=" * 60)
    print("Chapter 23 — Graph Representations")
    print("=" * 60)
    print(f"Vertices ({len(vertices)}): {vertices}")
    print(f"Edge list ({len(edges)} edges):")
    for edge in edges:
        print(f"  {edge}")
    print("\nAdjacency list:")
    print(json.dumps(adj_list, indent=2))
    print("\nAdjacency matrix (inf = no direct edge):")
    for label, row in zip(labels, matrix):
        formatted = [0 if x == 0 else ("inf" if x == float("inf") else x) for x in row]
        print(f"  {label}: {formatted}")
    print(f"\nNetworkX node count: {nx_graph.number_of_nodes()}")
    print(f"NetworkX edge count: {nx_graph.number_of_edges()}")
    print("=" * 60)


if __name__ == "__main__":
    main()
