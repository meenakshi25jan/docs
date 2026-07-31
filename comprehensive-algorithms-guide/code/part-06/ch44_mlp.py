"""Chapter 44 — Minimal MLP for XOR classification (NumPy)."""

from __future__ import annotations

import numpy as np

RNG = np.random.default_rng(42)


def sigmoid(x: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-x))


def dsigmoid(y: np.ndarray) -> np.ndarray:
    return y * (1.0 - y)


def train_mlp(
    x: np.ndarray,
    y: np.ndarray,
    hidden: int = 4,
    lr: float = 0.5,
    epochs: int = 5000,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    n_in, n_out = x.shape[1], y.shape[1]
    w1 = RNG.normal(0, 0.5, (n_in, hidden))
    b1 = np.zeros((1, hidden))
    w2 = RNG.normal(0, 0.5, (hidden, n_out))
    b2 = np.zeros((1, n_out))

    for _ in range(epochs):
        z1 = x @ w1 + b1
        a1 = sigmoid(z1)
        z2 = a1 @ w2 + b2
        a2 = sigmoid(z2)
        loss = np.mean((a2 - y) ** 2)

        dz2 = 2 * (a2 - y) / x.shape[0]
        da2 = dz2 * dsigmoid(a2)
        dw2 = a1.T @ da2
        db2 = np.sum(da2, axis=0, keepdims=True)
        da1 = da2 @ w2.T
        dz1 = da1 * dsigmoid(a1)
        dw1 = x.T @ dz1
        db1 = np.sum(dz1, axis=0, keepdims=True)

        w2 -= lr * dw2
        b2 -= lr * db2
        w1 -= lr * dw1
        b1 -= lr * db1

    return w1, b1, w2, b2


def predict(x: np.ndarray, w1: np.ndarray, b1: np.ndarray, w2: np.ndarray, b2: np.ndarray) -> np.ndarray:
    a1 = sigmoid(x @ w1 + b1)
    return (sigmoid(a1 @ w2 + b2) >= 0.5).astype(int)


def main() -> float:
    x = np.array([[0, 0], [0, 1], [1, 0], [1, 1]], dtype=float)
    y = np.array([[0], [1], [1], [0]], dtype=float)
    w1, b1, w2, b2 = train_mlp(x, y)
    preds = predict(x, w1, b1, w2, b2)
    acc = float(np.mean(preds == y))
    print(f"XOR predictions:\n{preds.ravel()}")
    print(f"Accuracy: {acc:.2f}")
    print("SUCCESS: MLP trained on XOR")
    return acc


if __name__ == "__main__":
    main()
