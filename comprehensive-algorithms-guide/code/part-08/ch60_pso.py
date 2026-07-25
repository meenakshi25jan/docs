"""Chapter 60 — Particle Swarm Optimization (from scratch)."""

from __future__ import annotations

import numpy as np

RNG = np.random.default_rng(42)


def sphere(x: np.ndarray) -> float:
    return float(np.sum(x**2))


def pso(
    dim: int = 5,
    particles: int = 20,
    iterations: int = 100,
    w: float = 0.7,
    c1: float = 1.5,
    c2: float = 1.5,
    bounds: tuple[float, float] = (-5.12, 5.12),
) -> tuple[np.ndarray, float]:
    lo, hi = bounds
    pos = RNG.uniform(lo, hi, size=(particles, dim))
    vel = RNG.uniform(-1, 1, size=(particles, dim))
    pbest = pos.copy()
    pbest_val = np.array([sphere(p) for p in pos])
    g_idx = int(np.argmin(pbest_val))
    gbest = pbest[g_idx].copy()
    gbest_val = float(pbest_val[g_idx])

    for _ in range(iterations):
        r1 = RNG.random(size=(particles, dim))
        r2 = RNG.random(size=(particles, dim))
        vel = w * vel + c1 * r1 * (pbest - pos) + c2 * r2 * (gbest - pos)
        pos = np.clip(pos + vel, lo, hi)
        vals = np.array([sphere(p) for p in pos])
        improved = vals < pbest_val
        pbest[improved] = pos[improved]
        pbest_val[improved] = vals[improved]
        g_idx = int(np.argmin(pbest_val))
        if pbest_val[g_idx] < gbest_val:
            gbest = pbest[g_idx].copy()
            gbest_val = float(pbest_val[g_idx])

    return gbest, gbest_val


def main() -> float:
    best, val = pso()
    print(f"Best position (first 3): {best[:3]}, fitness: {val:.6f}")
    print("SUCCESS: PSO optimization completed")
    return val


if __name__ == "__main__":
    main()
