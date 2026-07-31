"""Chapter 59 — Simplified PPO clip on a 1D control task."""

from __future__ import annotations

import numpy as np

RNG = np.random.default_rng(42)


def softmax(x: np.ndarray) -> np.ndarray:
    e = np.exp(x - x.max())
    return e / e.sum()


def rollout(theta: np.ndarray, steps: int = 30) -> tuple[list[int], list[float], list[float]]:
    actions, rewards, old_probs = [], [], []
    state = 0.0
    for _ in range(steps):
        logits = np.array([theta[0] * state, theta[1] * (1 - state)])
        probs = softmax(logits)
        a = int(RNG.choice(2, p=probs))
        state = min(1.0, max(0.0, state + (0.1 if a == 1 else -0.05)))
        r = state
        actions.append(a)
        rewards.append(r)
        old_probs.append(probs[a])
    return actions, rewards, old_probs


def train_ppo(epochs: int = 80, clip: float = 0.2) -> float:
    theta = np.array([0.0, 0.0])
    for _ in range(epochs):
        actions, rewards, old_probs = rollout(theta)
        returns = []
        g = 0.0
        for r in reversed(rewards):
            g = r + 0.95 * g
            returns.insert(0, g)
        returns = np.array(returns)
        returns = (returns - returns.mean()) / (returns.std() + 1e-8)
        state = 0.0
        for t, a in enumerate(actions):
            logits = np.array([theta[0] * state, theta[1] * (1 - state)])
            probs = softmax(logits)
            ratio = probs[a] / (old_probs[t] + 1e-8)
            clipped = np.clip(ratio, 1 - clip, 1 + clip)
            coef = min(ratio * returns[t], clipped * returns[t])
            grad = -probs.copy()
            grad[a] += 1
            theta += 0.05 * coef * grad
            state = min(1.0, max(0.0, state + (0.1 if a == 1 else -0.05)))
    return float(state)


def main() -> float:
    final_state = train_ppo()
    print(f"Final controlled state: {final_state:.3f}")
    print("SUCCESS: PPO training completed")
    return final_state


if __name__ == "__main__":
    main()
