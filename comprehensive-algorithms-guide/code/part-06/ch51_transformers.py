"""Chapter 51 — Scaled dot-product self-attention (NumPy)."""

from __future__ import annotations

import numpy as np

RNG = np.random.default_rng(42)


def softmax(x: np.ndarray, axis: int = -1) -> np.ndarray:
    e = np.exp(x - np.max(x, axis=axis, keepdims=True))
    return e / e.sum(axis=axis, keepdims=True)


def self_attention(x: np.ndarray, w_q: np.ndarray, w_k: np.ndarray, w_v: np.ndarray) -> np.ndarray:
    q = x @ w_q
    k = x @ w_k
    v = x @ w_v
    scores = q @ k.T / np.sqrt(q.shape[-1])
    weights = softmax(scores)
    return weights @ v


def main() -> float:
    seq_len, d_model = 4, 8
    x = RNG.normal(size=(seq_len, d_model))
    w_q = RNG.normal(0, 0.1, (d_model, d_model))
    w_k = RNG.normal(0, 0.1, (d_model, d_model))
    w_v = RNG.normal(0, 0.1, (d_model, d_model))
    out = self_attention(x, w_q, w_k, w_v)
    energy = float(np.mean(out**2))
    print(f"Attention output shape: {out.shape}, mean square: {energy:.4f}")
    print("SUCCESS: Transformer self-attention computed")
    return energy


if __name__ == "__main__":
    main()
