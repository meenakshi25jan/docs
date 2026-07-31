"""Chapter 63 — Firefly Algorithm (from scratch)."""

from __future__ import annotations

import numpy as np

RNG = np.random.default_rng(42)


def sphere(x: np.ndarray) -> float:
    return float(np.sum(x**2))


def firefly(
    dim: int = 5,
    n: int = 20,
    iterations: int = 80,
    alpha: float = 0.2,
    beta0: float = 1.0,
    gamma: float = 1.0,
    bounds: tuple[float, float] = (-5.0, 5.0),
) -> tuple[np.ndarray, float]:
    lo, hi = bounds
    x = RNG.uniform(lo, hi, size=(n, dim))
    intensity = np.array([1 / (1 + sphere(v)) for v in x])

    for _ in range(iterations):
        for i in range(n):
            for j in range(n):
                if intensity[j] > intensity[i]:
                    rij = np.linalg.norm(x[i] - x[j])
                    beta = beta0 * np.exp(-gamma * rij**2)
                    x[i] += beta * (x[j] - x[i]) + alpha * (RNG.random(dim) - 0.5)
            x[i] = np.clip(x[i], lo, hi)
            intensity[i] = 1 / (1 + sphere(x[i]))

    best_i = int(np.argmax(intensity))
    return x[best_i], sphere(x[best_i])


def main() -> float:
    best, val = firefly()
    print(f"Best fitness: {val:.6f}")
    print("SUCCESS: Firefly optimization completed")
    return val


if __name__ == "__main__":
    main()
