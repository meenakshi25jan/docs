"""Chapter 71 — Evolution Strategies (1+1)-ES (from scratch)."""

from __future__ import annotations

import numpy as np

RNG = np.random.default_rng(42)


def sphere(x: np.ndarray) -> float:
    return float(np.sum(x**2))


def evolutionary_strategy(
    dim: int = 6,
    generations: int = 200,
    sigma: float = 0.5,
    tau: float = 0.1,
) -> tuple[np.ndarray, float]:
    parent = RNG.normal(size=dim)
    parent_fit = sphere(parent)

    for _ in range(generations):
        child = parent + sigma * RNG.normal(size=dim)
        child_fit = sphere(child)
        if child_fit <= parent_fit:
            parent, parent_fit = child, child_fit
            sigma *= np.exp(tau)
        else:
            sigma *= np.exp(-tau)
        sigma = float(np.clip(sigma, 1e-4, 2.0))

    return parent, parent_fit


def main() -> float:
    best, val = evolutionary_strategy()
    print(f"Best fitness: {val:.6f}")
    print("SUCCESS: Evolutionary strategies completed")
    return val


if __name__ == "__main__":
    main()
