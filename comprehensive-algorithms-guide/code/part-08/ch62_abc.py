"""Chapter 62 — Artificial Bee Colony (from scratch)."""

from __future__ import annotations

import numpy as np

RNG = np.random.default_rng(42)


def rastrigin(x: np.ndarray) -> float:
    return float(10 * x.size + np.sum(x**2 - 10 * np.cos(2 * np.pi * x)))


def abc(
    dim: int = 5,
    food_sources: int = 16,
    limit: int = 20,
    iterations: int = 80,
    bounds: tuple[float, float] = (-5.12, 5.12),
) -> tuple[np.ndarray, float]:
    lo, hi = bounds
    solutions = RNG.uniform(lo, hi, size=(food_sources, dim))
    fitness = np.array([1 / (1 + rastrigin(s)) for s in solutions])
    trials = np.zeros(food_sources, dtype=int)

    for _ in range(iterations):
        for i in range(food_sources):
            partner = int(RNG.integers(food_sources))
            phi = RNG.uniform(-1, 1, size=dim)
            candidate = solutions[i] + phi * (solutions[i] - solutions[partner])
            candidate = np.clip(candidate, lo, hi)
            cand_fit = 1 / (1 + rastrigin(candidate))
            if cand_fit > fitness[i]:
                solutions[i] = candidate
                fitness[i] = cand_fit
                trials[i] = 0
            else:
                trials[i] += 1

        prob = fitness / fitness.sum()
        for _ in range(food_sources):
            i = int(RNG.choice(food_sources, p=prob))
            partner = int(RNG.integers(food_sources))
            phi = RNG.uniform(-1, 1, size=dim)
            candidate = solutions[i] + phi * (solutions[i] - solutions[partner])
            candidate = np.clip(candidate, lo, hi)
            cand_fit = 1 / (1 + rastrigin(candidate))
            if cand_fit > fitness[i]:
                solutions[i] = candidate
                fitness[i] = cand_fit
                trials[i] = 0
            else:
                trials[i] += 1

        for i in range(food_sources):
            if trials[i] >= limit:
                solutions[i] = RNG.uniform(lo, hi, size=dim)
                fitness[i] = 1 / (1 + rastrigin(solutions[i]))
                trials[i] = 0

    best_i = int(np.argmax(fitness))
    return solutions[best_i], rastrigin(solutions[best_i])


def main() -> float:
    best, val = abc()
    print(f"Best fitness: {val:.4f}")
    print("SUCCESS: ABC optimization completed")
    return val


if __name__ == "__main__":
    main()
