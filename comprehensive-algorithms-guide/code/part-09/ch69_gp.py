"""Chapter 69 — Genetic Programming for symbolic regression (from scratch)."""

from __future__ import annotations

import numpy as np

RNG = np.random.default_rng(42)
X = np.linspace(-1, 1, 20)
Y = X**2 + 0.1 * RNG.normal(size=X.shape)


def eval_tree(node: str, x: float) -> float:
    node = node.strip()
    if node == "x":
        return x
    if node.replace(".", "", 1).replace("-", "", 1).isdigit():
        return float(node)
    if node.startswith("(") and node.endswith(")"):
        inner = node[1:-1]
        depth = 0
        for i, ch in enumerate(inner):
            if ch == "(":
                depth += 1
            elif ch == ")":
                depth -= 1
            elif ch in "+*" and depth == 0:
                left, op, right = inner[:i], ch, inner[i + 1 :]
                l, r = eval_tree(left, x), eval_tree(right, x)
                return l + r if op == "+" else l * r
    raise ValueError(f"Bad node: {node}")


def mse(tree: str) -> float:
    preds = np.array([eval_tree(tree, float(x)) for x in X])
    return float(np.mean((preds - Y) ** 2))


def mutate(tree: str) -> str:
    options = ["(x+x)", "(x*x)", "x", "0.5", "(x*0.5)"]
    return str(RNG.choice(options))


def crossover(a: str, b: str) -> str:
    return a if RNG.random() < 0.5 else b


def gp(generations: int = 40, pop_size: int = 20) -> tuple[str, float]:
    population = ["(x*x)", "(x+x)", "x", "(x*0.5)", "(x+(x*x))"] * (pop_size // 5 + 1)
    population = population[:pop_size]

    for _ in range(generations):
        scored = [(mse(t), t) for t in population]
        scored.sort(key=lambda z: z[0])
        elites = [t for _, t in scored[:4]]
        new_pop = elites.copy()
        while len(new_pop) < pop_size:
            p1, p2 = RNG.choice(population, 2, replace=False)
            child = crossover(p1, p2)
            if RNG.random() < 0.3:
                child = mutate(child)
            new_pop.append(child)
        population = new_pop

    best = min(population, key=mse)
    return best, mse(best)


def main() -> float:
    tree, err = gp()
    print(f"Best tree: {tree}, MSE: {err:.4f}")
    print("SUCCESS: Genetic programming completed")
    return err


if __name__ == "__main__":
    main()
