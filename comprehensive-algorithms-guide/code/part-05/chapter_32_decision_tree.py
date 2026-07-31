#!/usr/bin/env python3
"""Chapter 32 — Decision Tree on Iris dataset."""

from __future__ import annotations

from sklearn.datasets import load_iris
from sklearn.tree import DecisionTreeClassifier

from ml_utils import classification_metrics, print_metrics, split_dataset


def main() -> None:
    data = load_iris()
    split = split_dataset(data.data, data.target)

    model = DecisionTreeClassifier(max_depth=4, random_state=42)
    model.fit(split.X_train, split.y_train)
    predictions = model.predict(split.X_test)
    metrics = classification_metrics(split.y_test, predictions)

    print("=" * 60)
    print("Chapter 32 — Decision Tree")
    print("Dataset: Iris (sklearn)")
    print("=" * 60)
    print(f"Tree depth: {model.get_depth()}, Leaves: {model.get_n_leaves()}")
    print_metrics("Test metrics", metrics)
    print("=" * 60)


if __name__ == "__main__":
    main()
