#!/usr/bin/env python3
"""Chapter 30 — Linear Regression on California Housing dataset."""

from __future__ import annotations

import numpy as np
from sklearn.datasets import fetch_california_housing
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler

from ml_utils import print_metrics, regression_metrics, split_dataset


def main() -> None:
    data = fetch_california_housing()
    split = split_dataset(data.data, data.target, feature_names=list(data.feature_names))

    scaler = StandardScaler()
    X_train = scaler.fit_transform(split.X_train)
    X_test = scaler.transform(split.X_test)

    model = LinearRegression()
    model.fit(X_train, split.y_train)
    predictions = model.predict(X_test)
    metrics = regression_metrics(split.y_test, predictions)

    print("=" * 60)
    print("Chapter 30 — Linear Regression")
    print("Dataset: California Housing (sklearn)")
    print("=" * 60)
    print(f"Samples: {data.data.shape[0]}, Features: {data.data.shape[1]}")
    print_metrics("Test metrics", metrics)
    print(f"Top coefficient feature: {data.feature_names[int(np.argmax(np.abs(model.coef_)))]}")
    print("=" * 60)


if __name__ == "__main__":
    main()
