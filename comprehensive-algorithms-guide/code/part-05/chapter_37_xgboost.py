#!/usr/bin/env python3
"""Chapter 37 — XGBoost on Diabetes dataset."""

from __future__ import annotations

from sklearn.datasets import load_diabetes
from xgboost import XGBRegressor

from ml_utils import print_metrics, regression_metrics, split_dataset


def main() -> None:
    data = load_diabetes()
    split = split_dataset(data.data, data.target, feature_names=list(data.feature_names))

    model = XGBRegressor(
        n_estimators=100,
        max_depth=4,
        learning_rate=0.1,
        random_state=42,
        verbosity=0,
    )
    model.fit(split.X_train, split.y_train)
    predictions = model.predict(split.X_test)
    metrics = regression_metrics(split.y_test, predictions)

    print("=" * 60)
    print("Chapter 37 — XGBoost")
    print("Dataset: Diabetes (sklearn)")
    print("=" * 60)
    print_metrics("Test metrics", metrics)
    print("=" * 60)


if __name__ == "__main__":
    main()
