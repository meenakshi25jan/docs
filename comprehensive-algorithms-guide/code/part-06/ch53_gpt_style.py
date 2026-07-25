"""Chapter 53 — GPT-style next-token prediction (toy)."""

from __future__ import annotations

import numpy as np

RNG = np.random.default_rng(42)
TOKENS = list("hello")
V = len(set(TOKENS)) + 5
CHARS = sorted(set(TOKENS))
IDX = {c: i for i, c in enumerate(CHARS)}


def softmax(x: np.ndarray) -> np.ndarray:
    e = np.exp(x - x.max())
    return e / e.sum()


def train_gpt(epochs: int = 2000, d: int = 16, lr: float = 0.05) -> np.ndarray:
    w_embed = RNG.normal(0, 0.1, (V, d))
    w_out = RNG.normal(0, 0.1, (d, V))
    seq = [IDX[c] for c in TOKENS]

    for _ in range(epochs):
        for t in range(len(seq) - 1):
            h = w_embed[seq[t]]
            logits = h @ w_out
            probs = softmax(logits)
            y = seq[t + 1]
            grad = probs
            grad[y] -= 1
            w_out -= lr * np.outer(h, grad)
            w_embed[seq[t]] -= lr * (grad @ w_out.T)

    h = w_embed[seq[-2]]
    return h @ w_out


def main() -> float:
    logits = train_gpt()
    pred = int(np.argmax(logits))
    inv = {i: c for c, i in IDX.items()}
    print(f"Next char prediction: '{inv.get(pred, '?')}'")
    print("SUCCESS: GPT-style autoregressive demo completed")
    return float(logits.max())


if __name__ == "__main__":
    main()
