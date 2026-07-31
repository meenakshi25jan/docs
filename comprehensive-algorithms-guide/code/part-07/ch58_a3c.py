"""Chapter 58 — Simplified A3C-style parallel workers on bandits."""

from __future__ import annotations

import numpy as np

RNG = np.random.default_rng(42)
N_ARMS = 4
TRUE_MEANS = np.array([0.1, 0.3, 0.9, 0.4])


def softmax(x: np.ndarray) -> np.ndarray:
    e = np.exp(x - x.max())
    return e / e.sum()


def worker_update(theta: np.ndarray, v: float, n_steps: int = 20) -> tuple[np.ndarray, float, float]:
    lr_pi, lr_v = 0.15, 0.15
    for _ in range(n_steps):
        probs = softmax(theta)
        a = int(RNG.choice(N_ARMS, p=probs))
        r = TRUE_MEANS[a] + RNG.normal(0, 0.05)
        adv = r - v
        v += lr_v * adv
        grad = -probs
        grad[a] += 1
        theta += lr_pi * adv * grad
    return theta, v, float(probs[np.argmax(TRUE_MEANS)])


def train_a3c(workers: int = 4, rounds: int = 50) -> float:
    global_theta = np.zeros(N_ARMS)
    global_v = 0.0
    for _ in range(rounds):
        deltas = []
        for w in range(workers):
            local_rng = np.random.default_rng(RNG.integers(1_000_000))
            theta = global_theta.copy()
            v = global_v
            probs = softmax(theta)
            a = int(local_rng.choice(N_ARMS, p=probs))
            r = TRUE_MEANS[a] + local_rng.normal(0, 0.05)
            adv = r - v
            grad = -probs
            grad[a] += 1
            deltas.append((adv * grad, adv))
        for d_theta, d_v in deltas:
            global_theta += 0.05 * d_theta
            global_v += 0.05 * d_v
    return float(softmax(global_theta)[np.argmax(TRUE_MEANS)])


def main() -> float:
    p = train_a3c()
    print(f"Best-arm probability: {p:.3f}")
    print("SUCCESS: A3C-style training completed")
    return p


if __name__ == "__main__":
    main()
