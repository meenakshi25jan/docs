"""Chapter 82 — Linear programming with SciPy."""

from __future__ import annotations

from scipy.optimize import linprog


def solve_lp() -> float:
    # Maximize 3x + 2y  => minimize -3x - 2y
    c = [-3.0, -2.0]
    a_ub = [[1.0, 1.0], [2.0, 1.0]]
    b_ub = [4.0, 5.0]
    bounds = [(0, None), (0, None)]
    result = linprog(c, A_ub=a_ub, b_ub=b_ub, bounds=bounds, method="highs")
    if not result.success:
        raise RuntimeError(result.message)
    return float(-result.fun)


def main() -> float:
    optimum = solve_lp()
    print(f"Optimal objective value: {optimum:.4f}")
    print("SUCCESS: Linear programming solved")
    return optimum


if __name__ == "__main__":
    main()
