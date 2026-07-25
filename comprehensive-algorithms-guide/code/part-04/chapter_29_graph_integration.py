#!/usr/bin/env python3
"""Chapter 29 — Graph algorithm selection and integration."""

from __future__ import annotations

import networkx as nx

from chapter_24_prims import prims_mst
from chapter_25_kruskals import kruskals_mst
from chapter_26_floyd_warshall import floyd_warshall, reconstruct_path
from chapter_27_topological_sort import build_course_graph, topological_sort_kahn
from chapter_28_pagerank import build_web_graph, pagerank
from graph_utils import Graph, adjacency_matrix, build_sample_graph


def dijkstra_reference(graph: nx.Graph, source: str) -> dict[str, float]:
    """
    Reference single-source shortest paths (covered in Part 2).

  See Part 2 for full Dijkstra and Bellman-Ford implementations.
    """
    return nx.single_source_dijkstra_path_length(graph, source, weight="weight")


def recommend_algorithm(problem: str) -> str:
    """Return a short recommendation string for common graph problems."""
    catalog = {
        "single_source_non_negative": "Dijkstra (Part 2, Ch. 11)",
        "single_source_negative_weights": "Bellman-Ford (Part 2, Ch. 12)",
        "all_pairs_shortest_paths": "Floyd-Warshall (Ch. 26)",
        "minimum_spanning_tree": "Prim (Ch. 24) or Kruskal (Ch. 25)",
        "task_scheduling": "Topological Sort (Ch. 27)",
        "web_authority": "PageRank (Ch. 28)",
        "reachability": "BFS/DFS (Part 2)",
    }
    return catalog.get(problem, "Analyze constraints: weighted?, directed?, dense?")


def main() -> None:
    """Compare graph algorithms on shared sample data."""
    graph = build_sample_graph()
    nx_graph = nx.Graph()
    for u, v, w in graph.edge_list():
        nx_graph.add_edge(u, v, weight=w)

    _, prim_total = prims_mst(graph)
    _, kruskal_total = kruskals_mst(graph)
    labels, matrix = adjacency_matrix(graph.vertices(), graph.edge_list())
    dist, nxt = floyd_warshall(labels, matrix)
    course_adj, indegree = build_course_graph()
    course_order = topological_sort_kahn(course_adj, indegree)
    ranks = pagerank(build_web_graph())
    dijkstra_dist = dijkstra_reference(nx_graph, "A")

    print("=" * 60)
    print("Chapter 29 — Graph Algorithms Integration")
    print("=" * 60)
    print(f"Prim MST total weight:     {prim_total}")
    print(f"Kruskal MST total weight:  {kruskal_total}")
    print(f"Floyd-Warshall A->E dist:  {dist[labels.index('A')][labels.index('E')]}")
    print(f"Topological order (first 3): {' -> '.join(course_order[:3])} ...")
    print(f"PageRank top node:         {max(ranks, key=ranks.get)}")
    print(f"Dijkstra from A (Part 2):  {dijkstra_dist}")
    print("\nAlgorithm recommendations:")
    for key in [
        "single_source_non_negative",
        "minimum_spanning_tree",
        "all_pairs_shortest_paths",
        "task_scheduling",
        "web_authority",
    ]:
        print(f"  {key}: {recommend_algorithm(key)}")
    print("=" * 60)


if __name__ == "__main__":
    main()
