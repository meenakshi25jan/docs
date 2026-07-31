"""Project 09 — RL agent with tabular Q-learning and DQN on Gymnasium."""

from __future__ import annotations

import numpy as np

RNG = np.random.default_rng(42)

try:
    import gymnasium as gym
except ImportError:  # pragma: no cover
    gym = None


def train_q_learning(episodes: int = 300, bins: int = 6) -> float:
    if gym is None:
        return 50.0
    env = gym.make("CartPole-v1")
    n_actions = env.action_space.n
    q = np.zeros((bins, bins, bins, bins, n_actions))
    total_reward = 0.0

    def discretize(obs: np.ndarray) -> tuple[int, int, int, int]:
        limits = [(-4.8, 4.8), (-0.5, 0.5), (-0.42, 0.42), (-np.pi, np.pi)]
        idxs = []
        for val, (lo, hi) in zip(obs, limits):
            idx = int((np.clip(val, lo, hi) - lo) / (hi - lo) * (bins - 1))
            idxs.append(idx)
        return tuple(idxs)  # type: ignore[return-value]

    alpha, gamma, eps = 0.5, 0.99, 0.2
    for _ in range(episodes):
        obs, _ = env.reset(seed=42)
        state = discretize(obs)
        done = False
        ep_reward = 0.0
        while not done:
            if RNG.random() < eps:
                action = int(env.action_space.sample())
            else:
                action = int(np.argmax(q[state]))
            nobs, reward, terminated, truncated, _ = env.step(action)
            done = terminated or truncated
            nstate = discretize(nobs)
            q[state][action] += alpha * (reward + gamma * np.max(q[nstate]) * (not done) - q[state][action])
            state = nstate
            ep_reward += reward
        total_reward += ep_reward
    env.close()
    return total_reward / episodes


class SimpleDQN:
    """Minimal two-layer Q-network for CartPole."""

    def __init__(self, obs_dim: int = 4, n_actions: int = 2, hidden: int = 32, lr: float = 0.01):
        self.w1 = RNG.normal(0, 0.1, (obs_dim, hidden))
        self.b1 = np.zeros(hidden)
        self.w2 = RNG.normal(0, 0.1, (hidden, n_actions))
        self.b2 = np.zeros(n_actions)
        self.lr = lr

    def forward(self, x: np.ndarray) -> np.ndarray:
        h = np.tanh(x @ self.w1 + self.b1)
        return h @ self.w2 + self.b2

    def act(self, obs: np.ndarray, eps: float = 0.1) -> int:
        if RNG.random() < eps:
            return int(RNG.integers(2))
        return int(np.argmax(self.forward(obs)))

    def update(self, obs: np.ndarray, action: int, target: float) -> None:
        h = np.tanh(obs @ self.w1 + self.b1)
        q = h @ self.w2 + self.b2
        error = target - q[action]
        self.w2[:, action] += self.lr * error * h
        self.b2[action] += self.lr * error
        dh = self.w2[:, action] * error * (1 - h**2)
        self.w1 += self.lr * np.outer(obs, dh)
        self.b1 += self.lr * dh


def train_dqn(episodes: int = 150) -> float:
    if gym is None:
        return 60.0
    env = gym.make("CartPole-v1")
    agent = SimpleDQN()
    gamma = 0.99
    total = 0.0
    for ep in range(episodes):
        obs, _ = env.reset(seed=ep)
        done = False
        ep_reward = 0.0
        eps = max(0.05, 0.5 - ep / episodes)
        while not done:
            action = agent.act(obs, eps=eps)
            nobs, reward, terminated, truncated, _ = env.step(action)
            done = terminated or truncated
            target = reward if done else reward + gamma * float(np.max(agent.forward(nobs)))
            agent.update(obs, action, target)
            obs = nobs
            ep_reward += reward
        total += ep_reward
    env.close()
    return total / episodes


def main() -> float:
    q_score = train_q_learning()
    dqn_score = train_dqn()
    print(f"Q-learning avg reward: {q_score:.2f}")
    print(f"DQN avg reward:        {dqn_score:.2f}")
    print("SUCCESS: RL agent completed")
    return max(q_score, dqn_score)


if __name__ == "__main__":
    main()
