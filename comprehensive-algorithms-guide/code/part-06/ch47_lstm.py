"""Chapter 47 — LSTM cell forward pass on a short sequence."""

from __future__ import annotations

import numpy as np

RNG = np.random.default_rng(42)


def sigmoid(x: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-np.clip(x, -20, 20)))


class LSTMCell:
    def __init__(self, input_dim: int, hidden_dim: int) -> None:
        scale = 0.1
        self.wf = RNG.normal(0, scale, (input_dim + hidden_dim, hidden_dim))
        self.wi = RNG.normal(0, scale, (input_dim + hidden_dim, hidden_dim))
        self.wc = RNG.normal(0, scale, (input_dim + hidden_dim, hidden_dim))
        self.wo = RNG.normal(0, scale, (input_dim + hidden_dim, hidden_dim))
        self.bf = np.zeros(hidden_dim)
        self.bi = np.zeros(hidden_dim)
        self.bc = np.zeros(hidden_dim)
        self.bo = np.zeros(hidden_dim)

    def forward(self, x: np.ndarray, h: np.ndarray, c: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        concat = np.concatenate([x, h])
        f = sigmoid(concat @ self.wf + self.bf)
        i = sigmoid(concat @ self.wi + self.bi)
        c_tilde = np.tanh(concat @ self.wc + self.bc)
        o = sigmoid(concat @ self.wo + self.bo)
        c_new = f * c + i * c_tilde
        h_new = o * np.tanh(c_new)
        return h_new, c_new


def run_sequence(seq: np.ndarray, cell: LSTMCell) -> np.ndarray:
    h = np.zeros(cell.wf.shape[1])
    c = np.zeros_like(h)
    outputs = []
    for x in seq:
        h, c = cell.forward(x, h, c)
        outputs.append(h.copy())
    return np.array(outputs)


def main() -> float:
    seq = RNG.normal(size=(5, 4))
    cell = LSTMCell(input_dim=4, hidden_dim=8)
    out = run_sequence(seq, cell)
    norm = float(np.linalg.norm(out))
    print(f"Output shape: {out.shape}, L2 norm: {norm:.4f}")
    print("SUCCESS: LSTM forward pass completed")
    return norm


if __name__ == "__main__":
    main()
