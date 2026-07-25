#!/usr/bin/env python3
"""Chapter 26 — Floyd-Warshall all-pairs shortest paths."""

from __future__ import annotations

from graph_utils import Graph, adjacency_matrix, build_sample_graph


def floyd_warshall(
    labels: list[str], matrix: list[list[float]]
) -> tuple[list[list[float]], list[list[int | None]]]:
    """
    Run Floyd-Warshall on adjacency matrix.

    Returns (distance_matrix, next_hop_matrix for path reconstruction).
    """
    n = len(labels)
    dist = [row[:] for row in matrix]
    nxt: list[list[int | None]] = [
        [j if i != j and matrix[i][j] != float("inf") else None for j in range(n)]
        for i in range(n)
    ]

    for k in range(n):
        for i in range(n):
            if dist[i][k] == float("inf"):
                continue
            for j in range(n):
                through = dist[i][k] + dist[k][j]
                if through < dist[i][j]:
                    dist[i][j] = through
                    nxt[i][j] = nxt[i][k]

    return dist, nxt


def reconstruct_path(
    labels: list[str], nxt: list[list[int | None]], start: str, end: str
) -> list[str]:
    """Reconstruct shortest path using next-hop matrix."""
    i, j = labels.index(start), labels.index(end)
    if nxt[i][j] is None:
        return []
    path = [labels[i]]
    while i != j:
        i = nxt[i][j]  # type: ignore[index]
        path.append(labels[i])
    return path


def main() -> None:
    """Compute all-pairs shortest paths on the sample graph."""
    graph = build_sample_graph()
    labels, matrix = adjacency_matrix(graph.vertices(), graph.edge_list())
    dist, nxt = floyd_warshall(labels, matrix)

    print("=" * 60)
    print("Chapter 26 — Floyd-Warshall All-Pairs Shortest Paths")
    print("=" * 60)
    print("Distance matrix:")
    header = "     " + "  ".join(f"{label:>5}" for label in labels)
    print(header)
    for label, row in zip(labels, dist):
        values = "  ".join(f"{d:5.0f}" if d != float("inf") else "  inf" for d in row)
        print(f"{label:>5} {values}")

    path = reconstruct_path(labels, nxt, "A", "E")
    print(f"\nShortest path A -> E: {' -> '.join(path)}")
    i, j = labels.index("A"), labels.index("E")
    print(f"Distance A -> E: {dist[i][j]}")
    print("=" * 60)


if __name__ == "__main__":
    main()
