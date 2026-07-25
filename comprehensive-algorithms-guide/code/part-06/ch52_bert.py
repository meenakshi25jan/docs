"""Chapter 52 — BERT-style masked token prediction (toy)."""

from __future__ import annotations

import numpy as np

RNG = np.random.default_rng(42)
VOCAB = ["the", "cat", "sat", "on", "mat"]
V = len(VOCAB)
IDX = {w: i for i, w in enumerate(VOCAB)}


def one_hot(i: int) -> np.ndarray:
    v = np.zeros(V)
    v[i] = 1.0
    return v


def train_masked_lm(epochs: int = 2000, d: int = 8, lr: float = 0.1) -> np.ndarray:
    w_embed = RNG.normal(0, 0.1, (V, d))
    w_out = RNG.normal(0, 0.1, (d, V))
    sentence = [IDX["the"], IDX["cat"], IDX["sat"], IDX["on"], IDX["mat"]]
    mask_pos = 2
    target = sentence[mask_pos]

    for _ in range(epochs):
        reps = w_embed[sentence]
        context = reps.mean(axis=0)
        logits = context @ w_out
        probs = np.exp(logits - logits.max())
        probs /= probs.sum()
        grad = probs - one_hot(target)
        w_out -= lr * np.outer(context, grad)
        context_grad = grad @ w_out.T
        for idx in sentence:
            w_embed[idx] -= lr * context_grad / len(sentence)

    logits = w_embed[sentence].mean(axis=0) @ w_out
    return logits


def main() -> float:
    logits = train_masked_lm()
    pred = int(np.argmax(logits))
    correct = pred == IDX["sat"]
    print(f"Predicted token: {VOCAB[pred]} (correct={correct})")
    print("SUCCESS: BERT-style masked LM demo completed")
    return float(correct)


if __name__ == "__main__":
    main()
