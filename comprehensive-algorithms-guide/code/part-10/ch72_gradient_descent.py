"""Chapter 72 — Batch gradient descent on quadratic."""

from __future__ import annotations

import numpy as np

RNG = np.random.default_rng(42)


def quadratic(w: np.ndarray) -> float:
    return float(np.sum(w**2))


def gradient_descent(
    dim: int = 3,
    lr: float = 0.1,
    steps: int = 100,
) -> tuple[np.ndarray, float]:
    w = RNG.normal(size=dim)
    for _ in range(steps):
        grad = 2 * w
        w -= lr * grad
    return w, quadratic(w)


def main() -> float:
    w, loss = gradient_descent()
    print(f"Final weights: {w}, loss: {loss:.6f}")
    print("SUCCESS: Gradient descent completed")
    return loss


if __name__ == "__main__":
    main()
