"""Chapter 81 — Dynamic programming knapsack."""

from __future__ import annotations


def knapsack_dp(weights: list[int], values: list[int], capacity: int) -> int:
    n = len(weights)
    dp = [[0] * (capacity + 1) for _ in range(n + 1)]
    for i in range(1, n + 1):
        w, v = weights[i - 1], values[i - 1]
        for c in range(capacity + 1):
            dp[i][c] = dp[i - 1][c]
            if w <= c:
                dp[i][c] = max(dp[i][c], dp[i - 1][c - w] + v)
    return dp[n][capacity]


def main() -> float:
    weights = [2, 3, 4, 5]
    values = [3, 4, 5, 8]
    best = knapsack_dp(weights, values, capacity=8)
    print(f"Maximum value: {best}")
    print("SUCCESS: Dynamic programming knapsack completed")
    return float(best)


if __name__ == "__main__":
    main()
