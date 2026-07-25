"""Chapter 65 — Bat Algorithm (from scratch)."""

from __future__ import annotations

import numpy as np

RNG = np.random.default_rng(42)


def sphere(x: np.ndarray) -> float:
    return float(np.sum(x**2))


def bat_algorithm(
    dim: int = 5,
    n: int = 20,
    iterations: int = 80,
    fmin: float = 0.0,
    fmax: float = 2.0,
    alpha: float = 0.9,
    gamma: float = 0.9,
    bounds: tuple[float, float] = (-5.0, 5.0),
) -> tuple[np.ndarray, float]:
    lo, hi = bounds
    x = RNG.uniform(lo, hi, size=(n, dim))
    v = np.zeros_like(x)
    freq = np.zeros(n)
    loudness = np.ones(n)
    pulse = RNG.random(n)

    best_i = int(np.argmin([sphere(b) for b in x]))
    best = x[best_i].copy()

    for t in range(iterations):
        for i in range(n):
            freq[i] = fmin + (fmax - fmin) * RNG.random()
            v[i] += (x[i] - best) * freq[i]
            x_new = x[i] + v[i]
            if RNG.random() > pulse[i]:
                x_new = best + 0.001 * RNG.normal(size=dim)
            x_new = np.clip(x_new, lo, hi)
            f_new = sphere(x_new)
            f_old = sphere(x[i])
            if f_new <= f_old and RNG.random() < loudness[i]:
                x[i] = x_new
                loudness[i] *= alpha
                pulse[i] *= (1 - np.exp(-gamma * t))
                if f_new < sphere(best):
                    best = x_new.copy()

    return best, sphere(best)


def main() -> float:
    best, val = bat_algorithm()
    print(f"Best fitness: {val:.6f}")
    print("SUCCESS: Bat algorithm completed")
    return val


if __name__ == "__main__":
    main()
