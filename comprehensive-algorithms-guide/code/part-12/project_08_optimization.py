"""Project 08 — Optimization with GA, PSO, simulated annealing, and DE."""

from __future__ import annotations

import numpy as np

RNG = np.random.default_rng(42)


def rastrigin(x: np.ndarray) -> float:
    n = x.size
    return float(10 * n + np.sum(x**2 - 10 * np.cos(2 * np.pi * x)))


def genetic_algorithm(dim: int = 5, pop: int = 40, generations: int = 80) -> float:
    population = RNG.uniform(-5.12, 5.12, size=(pop, dim))
    best = float("inf")
    for _ in range(generations):
        fitness = np.array([rastrigin(ind) for ind in population])
        best = min(best, float(fitness.min()))
        idx = np.argsort(fitness)[: pop // 2]
        parents = population[idx]
        children = []
        while len(children) < pop - len(parents):
            p1, p2 = parents[RNG.integers(len(parents), size=2)]
            alpha = RNG.random()
            child = alpha * p1 + (1 - alpha) * p2
            child += RNG.normal(0, 0.1, size=dim)
            children.append(np.clip(child, -5.12, 5.12))
        population = np.vstack([parents, np.array(children)])
    return best


def particle_swarm(dim: int = 5, particles: int = 30, iters: int = 80) -> float:
    pos = RNG.uniform(-5.12, 5.12, size=(particles, dim))
    vel = RNG.uniform(-1, 1, size=(particles, dim))
    pbest = pos.copy()
    pbest_val = np.array([rastrigin(p) for p in pos])
    gbest = pbest[np.argmin(pbest_val)].copy()
    gbest_val = float(pbest_val.min())
    for _ in range(iters):
        r1, r2 = RNG.random(size=(particles, dim)), RNG.random(size=(particles, dim))
        vel = 0.7 * vel + 1.5 * r1 * (pbest - pos) + 1.5 * r2 * (gbest - pos)
        pos = np.clip(pos + vel, -5.12, 5.12)
        vals = np.array([rastrigin(p) for p in pos])
        improved = vals < pbest_val
        pbest[improved] = pos[improved]
        pbest_val[improved] = vals[improved]
        if float(vals.min()) < gbest_val:
            gbest_val = float(vals.min())
            gbest = pos[np.argmin(vals)].copy()
    return gbest_val


def simulated_annealing(dim: int = 5, steps: int = 500, t0: float = 2.0) -> float:
    current = RNG.uniform(-5.12, 5.12, size=dim)
    current_e = rastrigin(current)
    best, best_e = current.copy(), current_e
    t = t0
    for _ in range(steps):
        proposal = np.clip(current + RNG.normal(0, 0.3, size=dim), -5.12, 5.12)
        pe = rastrigin(proposal)
        if pe < current_e or RNG.random() < np.exp(-(pe - current_e) / t):
            current, current_e = proposal, pe
            if pe < best_e:
                best, best_e = proposal.copy(), pe
        t *= 0.97
    return float(best_e)


def differential_evolution(dim: int = 5, pop: int = 30, generations: int = 80, f: float = 0.8, cr: float = 0.9) -> float:
    population = RNG.uniform(-5.12, 5.12, size=(pop, dim))
    for _ in range(generations):
        for i in range(pop):
            idxs = [j for j in range(pop) if j != i]
            a, b, c = population[RNG.choice(idxs, 3, replace=False)]
            mutant = np.clip(a + f * (b - c), -5.12, 5.12)
            trial = population[i].copy()
            cross = RNG.random(dim) < cr
            trial[cross] = mutant[cross]
            if rastrigin(trial) < rastrigin(population[i]):
                population[i] = trial
    return float(min(rastrigin(p) for p in population))


def main() -> float:
    ga = genetic_algorithm()
    pso = particle_swarm()
    sa = simulated_annealing()
    de = differential_evolution()
    print(f"GA best:  {ga:.4f}")
    print(f"PSO best: {pso:.4f}")
    print(f"SA best:  {sa:.4f}")
    print(f"DE best:  {de:.4f}")
    best = min(ga, pso, sa, de)
    print("SUCCESS: Optimization problem completed")
    return best


if __name__ == "__main__":
    main()
