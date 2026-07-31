"""Shared machine learning utilities for Part 5."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np
from sklearn.metrics import accuracy_score, f1_score, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split


@dataclass
class SplitData:
    """Train/test split with feature names."""

    X_train: np.ndarray
    X_test: np.ndarray
    y_train: np.ndarray
    y_test: np.ndarray
    feature_names: list[str] | None = None


def split_dataset(
    X: np.ndarray,
    y: np.ndarray,
    test_size: float = 0.25,
    random_state: int = 42,
    feature_names: list[str] | None = None,
) -> SplitData:
    """Stratified-friendly train/test split wrapper."""
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state
    )
    return SplitData(X_train, X_test, y_train, y_test, feature_names)


def regression_metrics(y_true: np.ndarray, y_pred: np.ndarray) -> dict[str, float]:
    """Compute common regression metrics."""
    return {
        "mse": float(mean_squared_error(y_true, y_pred)),
        "rmse": float(np.sqrt(mean_squared_error(y_true, y_pred))),
        "r2": float(r2_score(y_true, y_pred)),
    }


def classification_metrics(y_true: np.ndarray, y_pred: np.ndarray) -> dict[str, float]:
    """Compute common classification metrics."""
    return {
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "f1_macro": float(f1_score(y_true, y_pred, average="macro")),
    }


def print_metrics(title: str, metrics: dict[str, Any]) -> None:
    """Pretty-print metric dictionary."""
    print(f"\n{title}")
    for key, value in metrics.items():
        if isinstance(value, float):
            print(f"  {key}: {value:.4f}")
        else:
            print(f"  {key}: {value}")
