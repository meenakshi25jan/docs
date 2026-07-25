"""Chapter 68 — Genetic Algorithm (from scratch)."""

from __future__ import annotations

import numpy as np

RNG = np.random.default_rng(42)


def fitness(bits: np.ndarray) -> float:
    target = np.array([1, 0, 1, 1, 0, 1, 1, 0])
    return float(np.sum(bits == target))


def ga(
    pop_size: int = 40,
    gene_len: int = 8,
    generations: int = 50,
    mutation_rate: float = 0.05,
) -> tuple[np.ndarray, float]:
    pop = RNG.integers(0, 2, size=(pop_size, gene_len))

    for _ in range(generations):
        scores = np.array([fitness(ind) for ind in pop])
        probs = scores / (scores.sum() + 1e-9)
        new_pop = []
        while len(new_pop) < pop_size:
            p1 = pop[int(RNG.choice(pop_size, p=probs))]
            p2 = pop[int(RNG.choice(pop_size, p=probs))]
            point = int(RNG.integers(1, gene_len))
            c1 = np.concatenate([p1[:point], p2[point:]])
            c2 = np.concatenate([p2[:point], p1[point:]])
            for child in (c1, c2):
                for i in range(gene_len):
                    if RNG.random() < mutation_rate:
                        child[i] = 1 - child[i]
                new_pop.append(child)
        pop = np.array(new_pop[:pop_size])

    scores = np.array([fitness(ind) for ind in pop])
    best_i = int(np.argmax(scores))
    return pop[best_i], float(scores[best_i])


def main() -> float:
    best, score = ga()
    print(f"Best individual: {best}, fitness: {score}")
    print("SUCCESS: Genetic algorithm completed")
    return score


if __name__ == "__main__":
    main()
