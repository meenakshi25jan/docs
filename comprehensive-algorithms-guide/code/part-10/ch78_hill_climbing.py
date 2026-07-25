"""Chapter 78 — Hill climbing."""

from __future__ import annotations

import numpy as np

RNG = np.random.default_rng(42)


def objective(x: int) -> float:
    return float(-((x - 7) ** 2) + 50)


def hill_climbing(start: int = 0, max_steps: int = 50) -> tuple[int, float]:
    current = start
    current_val = objective(current)
    for _ in range(max_steps):
        neighbors = [current - 1, current + 1]
        best_neighbor = max(neighbors, key=objective)
        best_val = objective(best_neighbor)
        if best_val <= current_val:
            break
        current, current_val = best_neighbor, best_val
    return current, current_val


def main() -> float:
    x, val = hill_climbing()
    print(f"Peak at x={x}, value={val:.2f}")
    print("SUCCESS: Hill climbing completed")
    return val


if __name__ == "__main__":
    main()
