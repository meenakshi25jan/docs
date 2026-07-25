"""Tests for Part 2 — Searching algorithms."""

from __future__ import annotations

import math

import pytest

from a_star import a_star, manhattan_heuristic
from bellman_ford import bellman_ford
from binary_search import binary_search_iterative, binary_search_recursive, lower_bound
from bfs import bfs, bfs_levels, bfs_shortest_path_unweighted
from dfs import dfs_iterative, dfs_path, dfs_recursive
from dijkstra import dijkstra, reconstruct_path
from graph_types import Graph
from linear_search import linear_search, linear_search_all, linear_search_with_predicate


class TestLinearSearch:
    def test_found(self) -> None:
        assert linear_search([3, 1, 4, 1, 5], 4) == 2

    def test_not_found(self) -> None:
        assert linear_search([1, 2, 3], 9) == -1

    def test_all_indices(self) -> None:
        assert linear_search_all([1, 2, 1, 3, 1], 1) == [0, 2, 4]

    def test_predicate(self) -> None:
        assert linear_search_with_predicate([1, 3, 5, 6], lambda x: x % 2 == 0) == 3


class TestBinarySearch:
    data = [2, 4, 6, 8, 10, 12]

    def test_iterative_found(self) -> None:
        assert binary_search_iterative(self.data, 8) == 3

    def test_recursive_not_found(self) -> None:
        assert binary_search_recursive(self.data, 7) == -1

    def test_lower_bound(self) -> None:
        assert lower_bound(self.data, 7) == 3


@pytest.fixture
def sample_graph() -> Graph:
    graph = Graph()
    for edge in [("A", "B"), ("A", "C"), ("B", "D"), ("C", "D"), ("D", "E")]:
        graph.add_edge(*edge)
    return graph


class TestDFS:
    def test_recursive_and_iterative_same_nodes(self, sample_graph: Graph) -> None:
        recursive = dfs_recursive(sample_graph, "A")
        iterative = dfs_iterative(sample_graph, "A")
        assert set(recursive) == set(iterative) == {"A", "B", "C", "D", "E"}

    def test_path(self, sample_graph: Graph) -> None:
        path = dfs_path(sample_graph, "A", "E")
        assert path is not None
        assert path[0] == "A" and path[-1] == "E"


class TestBFS:
    def test_order_starts_with_start(self, sample_graph: Graph) -> None:
        order = bfs(sample_graph, "A")
        assert order[0] == "A"
        assert len(order) == 5

    def test_shortest_path(self, sample_graph: Graph) -> None:
        path = bfs_shortest_path_unweighted(sample_graph, "A", "E")
        assert path == ["A", "C", "D", "E"] or path == ["A", "B", "D", "E"]

    def test_levels(self, sample_graph: Graph) -> None:
        levels = bfs_levels(sample_graph, "A")
        assert levels["E"] == 3


class TestDijkstra:
    def test_distances(self) -> None:
        graph = Graph(directed=True)
        edges = [("A", "B", 4), ("A", "C", 2), ("B", "D", 5), ("C", "D", 8), ("D", "E", 2)]
        for s, t, w in edges:
            graph.add_edge(s, t, w)
        dist, pred = dijkstra(graph, "A")
        assert dist["E"] == 11
        path = reconstruct_path(pred, "A", "E")
        assert path == ["A", "B", "D", "E"]

    def test_negative_weight_raises(self) -> None:
        graph = Graph(directed=True)
        graph.add_edge("A", "B", -1)
        with pytest.raises(ValueError, match="non-negative"):
            dijkstra(graph, "A")


class TestBellmanFord:
    def test_negative_edge_no_cycle(self) -> None:
        graph = Graph(directed=True)
        graph.add_edge("A", "B", 1)
        graph.add_edge("B", "C", -2)
        graph.add_edge("A", "C", 4)
        dist, _, ok = bellman_ford(graph, "A")
        assert ok is True
        assert dist["C"] == -1

    def test_negative_cycle_detected(self) -> None:
        graph = Graph(directed=True)
        graph.add_edge("A", "B", 1)
        graph.add_edge("B", "C", -2)
        graph.add_edge("C", "A", -1)
        _, _, ok = bellman_ford(graph, "A")
        assert ok is False


class TestAStar:
    def test_grid_path(self) -> None:
        grid = Graph(directed=False)
        for x in range(2):
            for y in range(2):
                grid.add_node((x, y))
        grid.add_edge((0, 0), (1, 0), 1.0)
        grid.add_edge((0, 0), (0, 1), 1.0)
        grid.add_edge((1, 0), (1, 1), 1.0)
        grid.add_edge((0, 1), (1, 1), 1.0)
        path, cost = a_star(grid, (0, 0), (1, 1), manhattan_heuristic)
        assert path is not None
        assert path[0] == (0, 0) and path[-1] == (1, 1)
        assert cost == 2.0
