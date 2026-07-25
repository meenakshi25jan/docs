#!/usr/bin/env python3
"""Chapter 33 — Random Forest on Wine dataset."""

from __future__ import annotations

from sklearn.datasets import load_wine
from sklearn.ensemble import RandomForestClassifier

from ml_utils import classification_metrics, print_metrics, split_dataset


def main() -> None:
    data = load_wine()
    split = split_dataset(data.data, data.target)

    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(split.X_train, split.y_train)
    predictions = model.predict(split.X_test)
    metrics = classification_metrics(split.y_test, predictions)

    print("=" * 60)
    print("Chapter 33 — Random Forest")
    print("Dataset: Wine (sklearn)")
    print("=" * 60)
    print(f"Trees: {model.n_estimators}")
    importances = sorted(
        zip(data.feature_names, model.feature_importances_),
        key=lambda x: x[1],
        reverse=True,
    )
    print(f"Top feature: {importances[0][0]} ({importances[0][1]:.4f})")
    print_metrics("Test metrics", metrics)
    print("=" * 60)


if __name__ == "__main__":
    main()
