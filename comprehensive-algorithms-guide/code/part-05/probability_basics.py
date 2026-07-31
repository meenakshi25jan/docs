#!/usr/bin/env python3
"""Probability and statistics utilities for Chapter 2."""

from __future__ import annotations

import math
from collections import Counter
from typing import Sequence


def empirical_probability(outcomes: Sequence[str], event: str) -> float:
    """
    Estimate P(event) from observed outcomes.

    Args:
        outcomes: Sequence of categorical outcomes.
        event: Category whose frequency we measure.

    Returns:
        Fraction of outcomes equal to event, or 0.0 if outcomes is empty.
    """
    if not outcomes:
        return 0.0
    count: int = sum(1 for o in outcomes if o == event)
    return count / len(outcomes)


def bayes_posterior(
    prior: float,
    likelihood: float,
    evidence: float,
) -> float:
    """
    Compute posterior probability using Bayes' theorem.

    P(H|E) = P(E|H) * P(H) / P(E)

    Args:
        prior: P(H).
        likelihood: P(E|H).
        evidence: P(E).

    Returns:
        Posterior P(H|E).

    Raises:
        ValueError: If evidence is zero or probabilities are out of [0, 1].
    """
    if not 0.0 <= prior <= 1.0 or not 0.0 <= likelihood <= 1.0:
        raise ValueError("prior and likelihood must be in [0, 1]")
    if evidence <= 0.0:
        raise ValueError("evidence must be positive")
    return (likelihood * prior) / evidence


def mean_and_variance(values: Sequence[float]) -> tuple[float, float]:
    """
    Compute population mean and variance.

    Args:
        values: Numeric sequence.

    Returns:
        Tuple (mean, variance).

    Raises:
        ValueError: If values is empty.
    """
    if not values:
        raise ValueError("values must not be empty")
    n: int = len(values)
    mu: float = sum(values) / n
    var: float = sum((x - mu) ** 2 for x in values) / n
    return mu, var


def binomial_pmf(n: int, k: int, p: float) -> float:
    """
    Binomial probability mass: P(X = k) for X ~ Binomial(n, p).

    Args:
        n: Number of trials.
        k: Number of successes.
        p: Success probability per trial.

    Returns:
        Probability mass at k.

    Raises:
        ValueError: On invalid parameters.
    """
    if n < 0 or k < 0 or k > n:
        raise ValueError("require 0 <= k <= n")
    if not 0.0 <= p <= 1.0:
        raise ValueError("p must be in [0, 1]")
    coeff: float = math.comb(n, k)
    return coeff * (p**k) * ((1 - p) ** (n - k))


def summarize_distribution(values: Sequence[float]) -> dict[str, float]:
    """
    Summarize a numeric sample with mean, variance, min, and max.

    Args:
        values: Numeric sequence.

    Returns:
        Dictionary of summary statistics.
    """
    mu, var = mean_and_variance(values)
    return {
        "mean": mu,
        "variance": var,
        "std_dev": math.sqrt(var),
        "min": min(values),
        "max": max(values),
        "count": float(len(values)),
    }


def main() -> None:
    """Demonstrate probability and statistics."""
    rolls: list[str] = ["heads", "tails", "heads", "heads", "tails"]
    p_heads = empirical_probability(rolls, "heads")
    print(f"Empirical P(heads) from {rolls}: {p_heads:.3f}")

    # Spam filter toy example
    prior_spam = 0.10
    p_word_given_spam = 0.80
    p_word = 0.15
    posterior = bayes_posterior(prior_spam, p_word_given_spam, p_word)
    print(f"\nBayes posterior P(spam|keyword): {posterior:.4f}")

    samples = [2.0, 4.0, 4.0, 4.0, 5.0, 5.0, 7.0, 9.0]
    stats = summarize_distribution(samples)
    print("\nSample summary:")
    for key, val in stats.items():
        print(f"  {key}: {val:.4f}")

    n, k, p = 10, 3, 0.5
    pmf = binomial_pmf(n, k, p)
    print(f"\nBinomial({n}, {p}) at k={k}: {pmf:.6f}")

    freq = Counter(rolls)
    print(f"\nOutcome counts: {dict(freq)}")


if __name__ == "__main__":
    main()
