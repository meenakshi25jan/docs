"""Chapter 73 — Stochastic gradient descent for linear regression."""

from __future__ import annotations

import numpy as np

RNG = np.random.default_rng(42)


def generate_data(n: int = 100) -> tuple[np.ndarray, np.ndarray]:
    x = RNG.uniform(-1, 1, size=(n, 1))
    y = 3 * x.squeeze() + 2 + RNG.normal(0, 0.1, size=n)
    return x, y


def sgd(x: np.ndarray, y: np.ndarray, lr: float = 0.05, epochs: int = 50) -> tuple[float, float]:
    w, b = 0.0, 0.0
    n = x.shape[0]
    for _ in range(epochs):
        for i in range(n):
            pred = w * x[i, 0] + b
            err = pred - y[i]
            w -= lr * err * x[i, 0]
            b -= lr * err
    return w, b


def main() -> float:
    x, y = generate_data()
    w, b = sgd(x, y)
    mse = float(np.mean((w * x.squeeze() + b - y) ** 2))
    print(f"Learned w={w:.3f}, b={b:.3f}, MSE={mse:.4f}")
    print("SUCCESS: SGD completed")
    return mse


if __name__ == "__main__":
    main()
