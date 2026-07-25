"""Chapter 46 — Vanilla RNN next-character prediction."""

from __future__ import annotations

import numpy as np

RNG = np.random.default_rng(42)
TEXT = "abababc"
CHARS = sorted(set(TEXT))
IDX = {c: i for i, c in enumerate(CHARS)}
V = len(CHARS)


def one_hot(i: int) -> np.ndarray:
    v = np.zeros(V)
    v[i] = 1.0
    return v


def train_rnn(epochs: int = 800, hidden: int = 16, lr: float = 0.1) -> tuple[float, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    wxh = RNG.normal(0, 0.1, (V, hidden))
    whh = RNG.normal(0, 0.1, (hidden, hidden))
    why = RNG.normal(0, 0.1, (hidden, V))
    bh = np.zeros(hidden)
    by = np.zeros(V)
    h = np.zeros(hidden)

    for _ in range(epochs):
        loss = 0.0
        for t in range(len(TEXT) - 1):
            x = one_hot(IDX[TEXT[t]])
            y = one_hot(IDX[TEXT[t + 1]])
            h = np.tanh(x @ wxh + h @ whh + bh)
            logits = h @ why + by
            probs = np.exp(logits - np.max(logits))
            probs /= probs.sum()
            loss -= np.log(probs[IDX[TEXT[t + 1]]] + 1e-9)

            dy = probs - y
            dwhy = np.outer(h, dy)
            dby = dy
            dh = why @ dy * (1 - h**2)
            dwxh = np.outer(x, dh)
            dwhh = np.outer(h, dh)
            dbh = dh

            why -= lr * dwhy
            by -= lr * dby
            wxh -= lr * dwxh
            whh -= lr * dwhh
            bh -= lr * dbh

    return loss / (len(TEXT) - 1), wxh, whh, why, by


def main() -> float:
    loss, *_ = train_rnn()
    print(f"Average cross-entropy: {loss:.4f}")
    print("SUCCESS: RNN trained on tiny sequence")
    return loss


if __name__ == "__main__":
    main()
