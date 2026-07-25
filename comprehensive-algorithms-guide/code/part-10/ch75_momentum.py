"""Chapter 75 — Momentum optimizer."""

from __future__ import annotations

import numpy as np

RNG = np.random.default_rng(42)


def momentum_gd(
    dim: int = 4,
    lr: float = 0.05,
    beta: float = 0.9,
    steps: int = 120,
) -> tuple[np.ndarray, float]:
    w = RNG.normal(size=dim) * 3
    v = np.zeros(dim)
    for _ in range(steps):
        grad = 2 * w + 0.5 * np.sin(w)
        v = beta * v + lr * grad
        w -= v
    loss = float(np.sum(w**2))
    return w, loss


def main() -> float:
    w, loss = momentum_gd()
    print(f"Final loss: {loss:.6f}")
    print("SUCCESS: Momentum optimization completed")
    return loss


if __name__ == "__main__":
    main()
