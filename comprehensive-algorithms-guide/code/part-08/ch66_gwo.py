"""Chapter 66 — Grey Wolf Optimizer (from scratch)."""

from __future__ import annotations

import numpy as np

RNG = np.random.default_rng(42)


def sphere(x: np.ndarray) -> float:
    return float(np.sum(x**2))


def gwo(
    dim: int = 5,
    wolves: int = 20,
    iterations: int = 80,
    bounds: tuple[float, float] = (-5.12, 5.12),
) -> tuple[np.ndarray, float]:
    lo, hi = bounds
    pos = RNG.uniform(lo, hi, size=(wolves, dim))
    fitness = np.array([sphere(p) for p in pos])
    order = np.argsort(fitness)
    alpha, beta, delta = pos[order[0]], pos[order[1]], pos[order[2]]

    for t in range(iterations):
        a = 2 - 2 * t / iterations
        for i in range(wolves):
            for leader, name in ((alpha, "A"), (beta, "B"), (delta, "D")):
                r1, r2 = RNG.random(dim), RNG.random(dim)
                aa = 2 * a * r1 - a
                cc = 2 * r2
                d = np.abs(cc * leader - pos[i])
                pos[i] = leader - aa * d
            pos[i] = np.clip(pos[i], lo, hi)

        fitness = np.array([sphere(p) for p in pos])
        order = np.argsort(fitness)
        alpha, beta, delta = pos[order[0]], pos[order[1]], pos[order[2]]

    return alpha, float(sphere(alpha))


def main() -> float:
    best, val = gwo()
    print(f"Alpha wolf fitness: {val:.6f}")
    print("SUCCESS: GWO optimization completed")
    return val


if __name__ == "__main__":
    main()
