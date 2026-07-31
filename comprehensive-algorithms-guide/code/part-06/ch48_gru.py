"""Chapter 48 — GRU cell forward pass on a short sequence."""

from __future__ import annotations

import numpy as np

RNG = np.random.default_rng(42)


def sigmoid(x: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-np.clip(x, -20, 20)))


class GRUCell:
    def __init__(self, input_dim: int, hidden_dim: int) -> None:
        scale = 0.1
        dim = input_dim + hidden_dim
        self.wz = RNG.normal(0, scale, (dim, hidden_dim))
        self.wr = RNG.normal(0, scale, (dim, hidden_dim))
        self.wh = RNG.normal(0, scale, (dim, hidden_dim))
        self.bz = np.zeros(hidden_dim)
        self.br = np.zeros(hidden_dim)
        self.bh = np.zeros(hidden_dim)

    def forward(self, x: np.ndarray, h: np.ndarray) -> np.ndarray:
        concat = np.concatenate([x, h])
        z = sigmoid(concat @ self.wz + self.bz)
        r = sigmoid(concat @ self.wr + self.br)
        concat_h = np.concatenate([x, r * h])
        h_tilde = np.tanh(concat_h @ self.wh + self.bh)
        return (1 - z) * h + z * h_tilde


def run_sequence(seq: np.ndarray, cell: GRUCell) -> np.ndarray:
    h = np.zeros(cell.wz.shape[1])
    outputs = []
    for x in seq:
        h = cell.forward(x, h)
        outputs.append(h.copy())
    return np.array(outputs)


def main() -> float:
    seq = RNG.normal(size=(6, 3))
    cell = GRUCell(input_dim=3, hidden_dim=6)
    out = run_sequence(seq, cell)
    norm = float(np.linalg.norm(out))
    print(f"Output shape: {out.shape}, L2 norm: {norm:.4f}")
    print("SUCCESS: GRU forward pass completed")
    return norm


if __name__ == "__main__":
    main()
