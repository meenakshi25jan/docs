"""Chapter 77 — Simulated annealing."""

from __future__ import annotations

import numpy as np

RNG = np.random.default_rng(42)


def energy(x: np.ndarray) -> float:
    return float(np.sum(x**2) + 5 * np.sin(3 * x).sum())


def simulated_annealing(
    dim: int = 3,
    steps: int = 500,
    t0: float = 5.0,
    cooling: float = 0.97,
) -> tuple[np.ndarray, float]:
    current = RNG.uniform(-2, 2, size=dim)
    current_e = energy(current)
    best, best_e = current.copy(), current_e
    t = t0

    for _ in range(steps):
        proposal = current + RNG.normal(0, 0.2, size=dim)
        pe = energy(proposal)
        if pe < current_e or RNG.random() < np.exp(-(pe - current_e) / t):
            current, current_e = proposal, pe
            if pe < best_e:
                best, best_e = proposal.copy(), pe
        t *= cooling

    return best, best_e


def main() -> float:
    best, val = simulated_annealing()
    print(f"Best energy: {val:.4f}")
    print("SUCCESS: Simulated annealing completed")
    return val


if __name__ == "__main__":
    main()
