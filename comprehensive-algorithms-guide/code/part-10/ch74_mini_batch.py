"""Chapter 74 — Mini-batch gradient descent."""

from __future__ import annotations

import numpy as np

RNG = np.random.default_rng(42)


def train_minibatch(
    x: np.ndarray,
    y: np.ndarray,
    batch_size: int = 16,
    lr: float = 0.05,
    epochs: int = 40,
) -> tuple[float, float]:
    w, b = 0.0, 0.0
    n = x.shape[0]
    for _ in range(epochs):
        idx = RNG.permutation(n)
        for start in range(0, n, batch_size):
            batch = idx[start : start + batch_size]
            xb, yb = x[batch], y[batch]
            pred = w * xb.squeeze() + b
            err = pred - yb
            w -= lr * np.mean(err * xb.squeeze())
            b -= lr * np.mean(err)
    return w, b


def main() -> float:
    x = RNG.uniform(-1, 1, size=(200, 1))
    y = 2.5 * x.squeeze() + 1.0 + RNG.normal(0, 0.1, size=200)
    w, b = train_minibatch(x, y)
    mse = float(np.mean((w * x.squeeze() + b - y) ** 2))
    print(f"w={w:.3f}, b={b:.3f}, MSE={mse:.4f}")
    print("SUCCESS: Mini-batch GD completed")
    return mse


if __name__ == "__main__":
    main()
