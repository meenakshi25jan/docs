#!/usr/bin/env python3
"""Calculus and optimization utilities for Chapter 4."""

from __future__ import annotations

import math
from typing import Callable


def numerical_derivative(
    f: Callable[[float], float],
    x: float,
    h: float = 1e-5,
) -> float:
    """
    Approximate f'(x) using central finite differences.

    Args:
        f: Differentiable function.
        x: Point at which to estimate the derivative.
        h: Step size (small positive number).

    Returns:
        Approximate derivative value.

    Raises:
        ValueError: If h is not positive.
    """
    if h <= 0.0:
        raise ValueError("h must be positive")
    return (f(x + h) - f(x - h)) / (2.0 * h)


def gradient_descent(
    grad_f: Callable[[float], float],
    x0: float,
    learning_rate: float = 0.1,
    steps: int = 50,
) -> tuple[float, list[float]]:
    """
    Minimize a 1D function using gradient descent.

    Args:
        grad_f: Gradient (derivative) of the objective.
        x0: Starting point.
        learning_rate: Step size multiplier.
        steps: Number of iterations.

    Returns:
        Tuple of (final x, history of x values).

    Raises:
        ValueError: If learning_rate or steps are invalid.
    """
    if learning_rate <= 0.0:
        raise ValueError("learning_rate must be positive")
    if steps < 0:
        raise ValueError("steps must be non-negative")
    x: float = x0
    history: list[float] = [x]
    for _ in range(steps):
        x -= learning_rate * grad_f(x)
        history.append(x)
    return x, history


def newton_method(
    f: Callable[[float], float],
    df: Callable[[float], float],
    x0: float,
    tol: float = 1e-8,
    max_iter: int = 100,
) -> float:
    """
    Find a root of f using Newton's method.

    Args:
        f: Function whose root we seek.
        df: Derivative of f.
        x0: Initial guess.
        tol: Convergence tolerance on |f(x)|.
        max_iter: Maximum iterations.

    Returns:
        Approximate root.

    Raises:
        RuntimeError: If derivative is zero or max iterations exceeded.
    """
    x: float = x0
    for _ in range(max_iter):
        fx = f(x)
        if abs(fx) < tol:
            return x
        dfx = df(x)
        if dfx == 0.0:
            raise RuntimeError("derivative is zero")
        x -= fx / dfx
    raise RuntimeError("Newton method did not converge")


def main() -> None:
    """Demonstrate derivatives, gradient descent, and Newton's method."""
    square = lambda x: x * x
    x_point = 3.0
    deriv = numerical_derivative(square, x_point)
    print(f"d/dx(x^2) at x={x_point}: approximate = {deriv:.6f}, exact = {2 * x_point}")

    # Minimize (x - 2)^2 starting at x=10
    objective_grad = lambda x: 2.0 * (x - 2.0)
    final_x, history = gradient_descent(objective_grad, x0=10.0, learning_rate=0.3, steps=20)
    print(f"\nGradient descent minimum near x={final_x:.6f}")
    print(f"  first 5 iterates: {[round(h, 4) for h in history[:5]]}")
    print(f"  last 3 iterates:  {[round(h, 4) for h in history[-3:]]}")

    # Solve x^2 - 2 = 0
    f = lambda x: x * x - 2.0
    df = lambda x: 2.0 * x
    root = newton_method(f, df, x0=1.0)
    print(f"\nNewton root of x^2 - 2 = 0: {root:.10f}")
    print(f"sqrt(2) reference:            {math.sqrt(2):.10f}")


if __name__ == "__main__":
    main()
