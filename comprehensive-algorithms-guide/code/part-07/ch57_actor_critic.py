"""Chapter 57 — Actor-Critic on a bandit-like problem."""

from __future__ import annotations

import numpy as np

RNG = np.random.default_rng(42)
N_ARMS = 3
TRUE_MEANS = np.array([0.2, 0.8, 0.5])


def softmax(x: np.ndarray) -> np.ndarray:
    e = np.exp(x - x.max())
    return e / e.sum()


def train_actor_critic(steps: int = 1000, lr_pi: float = 0.1, lr_v: float = 0.1) -> float:
    theta = np.zeros(N_ARMS)
    v = 0.0
    for _ in range(steps):
        probs = softmax(theta)
        a = int(RNG.choice(N_ARMS, p=probs))
        reward = TRUE_MEANS[a] + RNG.normal(0, 0.1)
        td_error = reward - v
        v += lr_v * td_error
        grad = -probs
        grad[a] += 1
        theta += lr_pi * td_error * grad
    return float(probs[np.argmax(TRUE_MEANS)])


def main() -> float:
    best_prob = train_actor_critic()
    print(f"Probability on best arm: {best_prob:.3f}")
    print("SUCCESS: Actor-Critic completed")
    return best_prob


if __name__ == "__main__":
    main()
