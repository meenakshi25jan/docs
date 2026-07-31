"""Project 01 — Route planner with BFS, Dijkstra, and A*."""

from __future__ import annotations

import heapq
from collections import deque
from typing import Callable

Grid = list[list[int]]
Pos = tuple[int, int]


def neighbors(pos: Pos, grid: Grid) -> list[Pos]:
    r, c = pos
    rows, cols = len(grid), len(grid[0])
    result: list[Pos] = []
    for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
        nr, nc = r + dr, c + dc
        if 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] == 0:
            result.append((nr, nc))
    return result


def reconstruct(came_from: dict[Pos, Pos | None], goal: Pos) -> list[Pos]:
    path: list[Pos] = []
    cur: Pos | None = goal
    while cur is not None:
        path.append(cur)
        cur = came_from.get(cur)
    path.reverse()
    return path


def bfs(grid: Grid, start: Pos, goal: Pos) -> list[Pos]:
    queue: deque[Pos] = deque([start])
    came_from: dict[Pos, Pos | None] = {start: None}
    while queue:
        current = queue.popleft()
        if current == goal:
            return reconstruct(came_from, goal)
        for nxt in neighbors(current, grid):
            if nxt not in came_from:
                came_from[nxt] = current
                queue.append(nxt)
    return []


def dijkstra(grid: Grid, start: Pos, goal: Pos) -> list[Pos]:
    cost = {start: 0}
    came_from: dict[Pos, Pos | None] = {start: None}
    pq: list[tuple[float, Pos]] = [(0.0, start)]
    while pq:
        g, current = heapq.heappop(pq)
        if current == goal:
            return reconstruct(came_from, goal)
        if g > cost.get(current, float("inf")):
            continue
        for nxt in neighbors(current, grid):
            step = 1.0
            new_g = g + step
            if new_g < cost.get(nxt, float("inf")):
                cost[nxt] = new_g
                came_from[nxt] = current
                heapq.heappush(pq, (new_g, nxt))
    return []


def manhattan(a: Pos, b: Pos) -> float:
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def astar(grid: Grid, start: Pos, goal: Pos, heuristic: Callable[[Pos, Pos], float] = manhattan) -> list[Pos]:
    open_set: list[tuple[float, Pos]] = [(heuristic(start, goal), start)]
    g_score: dict[Pos, float] = {start: 0.0}
    came_from: dict[Pos, Pos | None] = {start: None}
    closed: set[Pos] = set()

    while open_set:
        _, current = heapq.heappop(open_set)
        if current in closed:
            continue
        if current == goal:
            return reconstruct(came_from, goal)
        closed.add(current)
        for nxt in neighbors(current, grid):
            tentative = g_score[current] + 1.0
            if tentative < g_score.get(nxt, float("inf")):
                came_from[nxt] = current
                g_score[nxt] = tentative
                f = tentative + heuristic(nxt, goal)
                heapq.heappush(open_set, (f, nxt))
    return []


def demo_grid() -> Grid:
    return [
        [0, 0, 0, 0, 0],
        [0, 1, 1, 0, 0],
        [0, 0, 0, 0, 0],
        [0, 0, 1, 1, 0],
        [0, 0, 0, 0, 0],
    ]


def main() -> int:
    grid = demo_grid()
    start, goal = (0, 0), (4, 4)
    path_bfs = bfs(grid, start, goal)
    path_dij = dijkstra(grid, start, goal)
    path_astar = astar(grid, start, goal)
    print(f"BFS path length:      {len(path_bfs)}")
    print(f"Dijkstra path length: {len(path_dij)}")
    print(f"A* path length:       {len(path_astar)}")
    print("SUCCESS: Route planner completed")
    return len(path_astar)


if __name__ == "__main__":
    main()
