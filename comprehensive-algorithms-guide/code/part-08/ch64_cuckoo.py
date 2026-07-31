"""Chapter 64 — Cuckoo Search with Lévy flights (from scratch)."""

from __future__ import annotations

import math

import numpy as np

RNG = np.random.default_rng(42)


def ackley(x: np.ndarray) -> float:
    d = x.size
    return float(
        -20 * np.exp(-0.2 * np.sqrt(np.mean(x**2)))
        - np.exp(np.mean(np.cos(2 * np.pi * x)))
        + 20
        + np.e
    )


def levy_step(dim: int, beta: float = 1.5) -> np.ndarray:
    sigma = (
        math.gamma(1 + beta)
        * np.sin(np.pi * beta / 2)
        / (math.gamma((1 + beta) / 2) * beta * 2 ** ((beta - 1) / 2))
    ) ** (1 / beta)
    u = RNG.normal(0, sigma, size=dim)
    v = RNG.normal(0, 1, size=dim)
    return u / (np.abs(v) ** (1 / beta) + 1e-9)


def cuckoo_search(
    dim: int = 5,
    n: int = 15,
    pa: float = 0.25,
    iterations: int = 80,
    bounds: tuple[float, float] = (-5.0, 5.0),
) -> tuple[np.ndarray, float]:
    lo, hi = bounds
    nests = RNG.uniform(lo, hi, size=(n, dim))
    fitness = np.array([ackley(x) for x in nests])

    for _ in range(iterations):
        i = int(RNG.integers(n))
        step = levy_step(dim)
        new = nests[i] + 0.01 * step * (nests[i] - lo)
        new = np.clip(new, lo, hi)
        f_new = ackley(new)
        if f_new < fitness[i]:
            nests[i] = new
            fitness[i] = f_new

        worst = np.argsort(fitness)[-int(pa * n) :]
        nests[worst] = RNG.uniform(lo, hi, size=(worst.size, dim))
        fitness[worst] = np.array([ackley(x) for x in nests[worst]])

    best_i = int(np.argmin(fitness))
    return nests[best_i], float(fitness[best_i])


def main() -> float:
    best, val = cuckoo_search()
    print(f"Best fitness: {val:.4f}")
    print("SUCCESS: Cuckoo search completed")
    return val


if __name__ == "__main__":
    main()
