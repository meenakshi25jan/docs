"""Chapter 61 — Ant Colony Optimization for tiny TSP (from scratch)."""

from __future__ import annotations

import numpy as np

RNG = np.random.default_rng(42)


def tour_length(dist: np.ndarray, tour: list[int]) -> float:
    total = 0.0
    for i in range(len(tour)):
        total += dist[tour[i], tour[(i + 1) % len(tour)]]
    return total


def aco(
    dist: np.ndarray,
    n_ants: int = 10,
    iterations: int = 60,
    alpha: float = 1.0,
    beta: float = 3.0,
    rho: float = 0.5,
    q: float = 100.0,
) -> tuple[list[int], float]:
    n = dist.shape[0]
    pheromone = np.ones((n, n))
    best_tour = list(range(n))
    best_len = tour_length(dist, best_tour)

    for _ in range(iterations):
        all_tours = []
        for _ in range(n_ants):
            unvisited = set(range(1, n))
            tour = [0]
            while unvisited:
                i = tour[-1]
                candidates = sorted(unvisited)
                weights = []
                for j in candidates:
                    tau = pheromone[i, j] ** alpha
                    eta = (1.0 / (dist[i, j] + 1e-9)) ** beta
                    weights.append(tau * eta)
                weights = np.array(weights)
                weights /= weights.sum()
                j = int(RNG.choice(candidates, p=weights))
                tour.append(j)
                unvisited.remove(j)
            all_tours.append(tour)
            length = tour_length(dist, tour)
            if length < best_len:
                best_len = length
                best_tour = tour

        pheromone *= 1 - rho
        for tour in all_tours:
            d = tour_length(dist, tour)
            for i in range(n):
                a, b = tour[i], tour[(i + 1) % n]
                pheromone[a, b] += q / d
                pheromone[b, a] += q / d

    return best_tour, best_len


def main() -> float:
    cities = RNG.uniform(0, 1, size=(6, 2))
    dist = np.linalg.norm(cities[:, None, :] - cities[None, :, :], axis=2)
    np.fill_diagonal(dist, 1e9)
    tour, length = aco(dist)
    print(f"Best tour: {tour}, length: {length:.4f}")
    print("SUCCESS: ACO TSP completed")
    return length


if __name__ == "__main__":
    main()
