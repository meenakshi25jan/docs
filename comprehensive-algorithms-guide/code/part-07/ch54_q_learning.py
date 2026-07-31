"""Chapter 54 — Tabular Q-Learning on a tiny gridworld."""

from __future__ import annotations

import numpy as np

RNG = np.random.default_rng(42)
GRID = 3
GOAL = (2, 2)
ACTIONS = [(-1, 0), (1, 0), (0, -1), (0, 1)]  # up, down, left, right


def step(state: tuple[int, int], action: int) -> tuple[tuple[int, int], float, bool]:
    r, c = state
    dr, dc = ACTIONS[action]
    nr, nc = max(0, min(GRID - 1, r + dr)), max(0, min(GRID - 1, c + dc))
    ns = (nr, nc)
    if ns == GOAL:
        return ns, 1.0, True
    return ns, -0.01, False


def train_q_learning(episodes: int = 500, alpha: float = 0.5, gamma: float = 0.95, eps: float = 0.2) -> np.ndarray:
    q = np.zeros((GRID, GRID, len(ACTIONS)))
    for _ in range(episodes):
        state = (0, 0)
        done = False
        while not done:
            r, c = state
            if RNG.random() < eps:
                a = int(RNG.integers(len(ACTIONS)))
            else:
                a = int(np.argmax(q[r, c]))
            ns, reward, done = step(state, a)
            nr, nc = ns
            q[r, c, a] += alpha * (reward + gamma * np.max(q[nr, nc]) * (not done) - q[r, c, a])
            state = ns
    return q


def main() -> float:
    q = train_q_learning()
    best = float(np.max(q[0, 0]))
    print(f"Q*(start, best action) = {best:.3f}")
    print("SUCCESS: Q-Learning completed")
    return best


if __name__ == "__main__":
    main()
