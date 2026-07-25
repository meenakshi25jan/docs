"""Chapter 56 — Deep Q-Network on CartPole-like linear features."""

from __future__ import annotations

import numpy as np

RNG = np.random.default_rng(42)


def sigmoid(x: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-x))


class LinearDQN:
    def __init__(self, state_dim: int, n_actions: int) -> None:
        self.w = RNG.normal(0, 0.1, (state_dim, n_actions))
        self.b = np.zeros(n_actions)

    def q_values(self, state: np.ndarray) -> np.ndarray:
        return state @ self.w + self.b

    def act(self, state: np.ndarray, eps: float) -> int:
        if RNG.random() < eps:
            return int(RNG.integers(self.b.shape[0]))
        return int(np.argmax(self.q_values(state)))

    def update(self, s: np.ndarray, a: int, target: float, lr: float = 0.05) -> None:
        q = self.q_values(s)
        error = target - q[a]
        self.w[:, a] += lr * error * s
        self.b[a] += lr * error


def simple_env_step(state: np.ndarray, action: int) -> tuple[np.ndarray, float, bool]:
  # Toy dynamics: move toward target position 1.0
    pos, vel = state
    force = 1.0 if action == 1 else -1.0
    vel = 0.9 * vel + 0.1 * force
    pos = pos + vel
    reward = -abs(1.0 - pos)
    done = abs(pos - 1.0) < 0.05
    return np.array([pos, vel]), reward, done


def train_dqn(steps: int = 400) -> float:
    agent = LinearDQN(2, 2)
    state = np.array([0.0, 0.0])
    total_reward = 0.0
    for t in range(steps):
        a = agent.act(state, eps=max(0.05, 0.5 - t / steps))
        ns, r, done = simple_env_step(state, a)
        target = r if done else r + 0.95 * np.max(agent.q_values(ns))
        agent.update(state, a, target)
        state = np.array([0.0, 0.0]) if done else ns
        total_reward += r
    return total_reward / steps


def main() -> float:
    avg_r = train_dqn()
    print(f"Average step reward: {avg_r:.4f}")
    print("SUCCESS: DQN training completed")
    return avg_r


if __name__ == "__main__":
    main()
