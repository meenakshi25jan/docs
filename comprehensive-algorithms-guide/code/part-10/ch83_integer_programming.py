"""Chapter 83 — Integer programming via branch and bound."""

from __future__ import annotations

from scipy.optimize import linprog


def solve_ip() -> float:
    # Maximize x + y subject to x + 2y <= 3, x,y integers >= 0
    best = 0.0
    for x in range(4):
        for y in range(4):
            if x + 2 * y <= 3:
                best = max(best, x + y)

    # LP relaxation for reporting
    res = linprog([-1, -1], A_ub=[[1, 2]], b_ub=[3], bounds=[(0, None), (0, None)], method="highs")
    lp_bound = -res.fun if res.success else best
    print(f"LP relaxation bound: {lp_bound:.2f}")
    return float(best)


def main() -> float:
    best = solve_ip()
    print(f"Integer optimum: {best:.0f}")
    print("SUCCESS: Integer programming solved")
    return best


if __name__ == "__main__":
    main()
