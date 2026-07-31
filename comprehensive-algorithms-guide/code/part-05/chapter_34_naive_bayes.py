#!/usr/bin/env python3
"""Chapter 34 — Naive Bayes on Digits dataset."""

from __future__ import annotations

from sklearn.datasets import load_digits
from sklearn.naive_bayes import GaussianNB

from ml_utils import classification_metrics, print_metrics, split_dataset


def main() -> None:
    data = load_digits()
    split = split_dataset(data.data, data.target)

    model = GaussianNB()
    model.fit(split.X_train, split.y_train)
    predictions = model.predict(split.X_test)
    metrics = classification_metrics(split.y_test, predictions)

    print("=" * 60)
    print("Chapter 34 — Naive Bayes (Gaussian)")
    print("Dataset: Digits (sklearn)")
    print("=" * 60)
    print(f"Classes: {len(data.target_names)}")
    print_metrics("Test metrics", metrics)
    print("=" * 60)


if __name__ == "__main__":
    main()
