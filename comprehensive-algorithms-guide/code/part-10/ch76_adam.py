"""Chapter 76 — Adam optimizer."""

from __future__ import annotations

import numpy as np

RNG = np.random.default_rng(42)


def adam(
    dim: int = 4,
    lr: float = 0.1,
    beta1: float = 0.9,
    beta2: float = 0.999,
    eps: float = 1e-8,
    steps: int = 150,
) -> tuple[np.ndarray, float]:
    w = RNG.normal(size=dim) * 2
    m = np.zeros(dim)
    v = np.zeros(dim)
    for t in range(1, steps + 1):
        grad = 2 * w
        m = beta1 * m + (1 - beta1) * grad
        v = beta2 * v + (1 - beta2) * grad**2
        m_hat = m / (1 - beta1**t)
        v_hat = v / (1 - beta2**t)
        w -= lr * m_hat / (np.sqrt(v_hat) + eps)
    return w, float(np.sum(w**2))


def main() -> float:
    w, loss = adam()
    print(f"Final loss: {loss:.6f}")
    print("SUCCESS: Adam optimization completed")
    return loss


if __name__ == "__main__":
    main()
