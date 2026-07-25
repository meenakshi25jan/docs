"""Chapter 70 — Differential Evolution (from scratch)."""

from __future__ import annotations

import numpy as np

RNG = np.random.default_rng(42)


def rosenbrock(x: np.ndarray) -> float:
    return float(np.sum(100 * (x[1:] - x[:-1] ** 2) ** 2 + (1 - x[:-1]) ** 2))


def differential_evolution(
    dim: int = 4,
    pop_size: int = 20,
    generations: int = 100,
    f: float = 0.8,
    cr: float = 0.9,
    bounds: tuple[float, float] = (-2.0, 2.0),
) -> tuple[np.ndarray, float]:
    lo, hi = bounds
    pop = RNG.uniform(lo, hi, size=(pop_size, dim))
    fitness = np.array([rosenbrock(v) for v in pop])

    for _ in range(generations):
        for i in range(pop_size):
            idxs = [j for j in range(pop_size) if j != i]
            a, b, c = pop[RNG.choice(idxs, 3, replace=False)]
            mutant = np.clip(a + f * (b - c), lo, hi)
            trial = pop[i].copy()
            cross = RNG.random(dim) < cr
            if not np.any(cross):
                cross[int(RNG.integers(dim))] = True
            trial = np.where(cross, mutant, trial)
            f_trial = rosenbrock(trial)
            if f_trial < fitness[i]:
                pop[i] = trial
                fitness[i] = f_trial

    best_i = int(np.argmin(fitness))
    return pop[best_i], float(fitness[best_i])


def main() -> float:
    best, val = differential_evolution()
    print(f"Best fitness: {val:.4f}")
    print("SUCCESS: Differential evolution completed")
    return val


if __name__ == "__main__":
    main()
