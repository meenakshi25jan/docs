"""Tests for Part 4 — Graph Algorithms (Chapters 23-29)."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

CODE_DIR = Path(__file__).resolve().parents[2] / "code" / "part-04"


def _run_script(name: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(CODE_DIR / name)],
        capture_output=True,
        text=True,
        check=False,
    )


@pytest.mark.parametrize(
    "script",
    [
        "chapter_23_graph_representations.py",
        "chapter_24_prims.py",
        "chapter_25_kruskals.py",
        "chapter_26_floyd_warshall.py",
        "chapter_27_topological_sort.py",
        "chapter_28_pagerank.py",
        "chapter_29_graph_integration.py",
    ],
)
def test_chapter_scripts_exit_zero(script: str) -> None:
    result = _run_script(script)
    assert result.returncode == 0, result.stderr
    assert "=" * 60 in result.stdout


def test_prims_and_kruskal_same_weight() -> None:
    from chapter_24_prims import prims_mst
    from chapter_25_kruskals import kruskals_mst
    from graph_utils import build_sample_graph

    graph = build_sample_graph()
    _, prim_total = prims_mst(graph)
    _, kruskal_total = kruskals_mst(graph)
    assert prim_total == kruskal_total


def test_floyd_warshall_shortest_path() -> None:
    from chapter_26_floyd_warshall import floyd_warshall, reconstruct_path
    from graph_utils import adjacency_matrix, build_sample_graph

    graph = build_sample_graph()
    labels, matrix = adjacency_matrix(graph.vertices(), graph.edge_list())
    dist, nxt = floyd_warshall(labels, matrix)
    path = reconstruct_path(labels, nxt, "A", "E")
    assert path[0] == "A" and path[-1] == "E"
    i, j = labels.index("A"), labels.index("E")
    assert dist[i][j] == 10.0


def test_topological_sort_length() -> None:
    from chapter_27_topological_sort import build_course_graph, topological_sort_kahn

    adjacency, indegree = build_course_graph()
    order = topological_sort_kahn(adjacency, indegree)
    assert len(order) == len(indegree)
    assert order[0] == "Intro"


def test_pagerank_sums_to_one() -> None:
    from chapter_28_pagerank import build_web_graph, pagerank

    ranks = pagerank(build_web_graph())
    assert abs(sum(ranks.values()) - 1.0) < 1e-5


def test_graph_representations_networkx() -> None:
    from chapter_23_graph_representations import networkx_from_graph
    from graph_utils import build_sample_graph

    nx_graph = networkx_from_graph(build_sample_graph())
    assert nx_graph.number_of_nodes() == 5
    assert nx_graph.number_of_edges() == 7
