"""Chapter 79 — Tabu search for small TSP."""

from __future__ import annotations

import numpy as np

RNG = np.random.default_rng(42)


def tour_length(dist: np.ndarray, tour: list[int]) -> float:
    return sum(dist[tour[i], tour[(i + 1) % len(tour)]] for i in range(len(tour)))


def neighbors(tour: list[int]) -> list[list[int]]:
    n = len(tour)
    result = []
    for i in range(n):
        for j in range(i + 1, n):
            new = tour.copy()
            new[i], new[j] = new[j], new[i]
            result.append(new)
    return result


def tabu_search(dist: np.ndarray, iterations: int = 80, tenure: int = 4) -> tuple[list[int], float]:
    n = dist.shape[0]
    current = list(range(n))
    RNG.shuffle(current)
    best = current.copy()
    best_len = tour_length(dist, best)
    tabu: dict[tuple[int, int], int] = {}

    for it in range(iterations):
        best_move = None
        best_move_len = float("inf")
        for cand in neighbors(current):
            length = tour_length(dist, cand)
            move = tuple(sorted((cand[0], cand[-1])))
            is_tabu = tabu.get(move, -1) > it
            if length < best_move_len and (not is_tabu or length < best_len):
                best_move = cand
                best_move_len = length
        if best_move is None:
            break
        current = best_move
        move = tuple(sorted((current[0], current[-1])))
        tabu[move] = it + tenure
        if best_move_len < best_len:
            best, best_len = current.copy(), best_move_len

    return best, best_len


def main() -> float:
    cities = RNG.uniform(0, 1, size=(5, 2))
    dist = np.linalg.norm(cities[:, None, :] - cities[None, :, :], axis=2)
    tour, length = tabu_search(dist)
    print(f"Tour: {tour}, length: {length:.4f}")
    print("SUCCESS: Tabu search completed")
    return length


if __name__ == "__main__":
    main()
