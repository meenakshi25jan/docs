"""Chapter 67 — Whale Optimization Algorithm (from scratch)."""

from __future__ import annotations

import numpy as np

RNG = np.random.default_rng(42)


def sphere(x: np.ndarray) -> float:
    return float(np.sum(x**2))


def woa(
    dim: int = 5,
    whales: int = 20,
    iterations: int = 80,
    bounds: tuple[float, float] = (-5.12, 5.12),
) -> tuple[np.ndarray, float]:
    lo, hi = bounds
    pos = RNG.uniform(lo, hi, size=(whales, dim))
    fitness = np.array([sphere(p) for p in pos])
    best_idx = int(np.argmin(fitness))
    best = pos[best_idx].copy()

    for t in range(iterations):
        a = 2 - t * (2 / iterations)
        for i in range(whales):
            r = RNG.random()
            aa = 2 * a * r - a
            c = 2 * RNG.random()
            p = RNG.random()
            if p < 0.5:
                if abs(aa) < 1:
                    d = abs(c * best - pos[i])
                    pos[i] = best - aa * d
                else:
                    rand = pos[int(RNG.integers(whales))]
                    d = abs(c * rand - pos[i])
                    pos[i] = rand - aa * d
            else:
                d = abs(best - pos[i])
                b = 1.0
                l = RNG.uniform(-1, 1)
                pos[i] = d * np.exp(b * l) * np.cos(2 * np.pi * l) + best
            pos[i] = np.clip(pos[i], lo, hi)

        fitness = np.array([sphere(p) for p in pos])
        best_idx = int(np.argmin(fitness))
        if fitness[best_idx] < sphere(best):
            best = pos[best_idx].copy()

    return best, float(sphere(best))


def main() -> float:
    best, val = woa()
    print(f"Best fitness: {val:.6f}")
    print("SUCCESS: WOA optimization completed")
    return val


if __name__ == "__main__":
    main()
