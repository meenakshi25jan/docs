#!/usr/bin/env python3
"""Chapter 36 — k-Nearest Neighbors on Iris dataset."""

from __future__ import annotations

from sklearn.datasets import load_iris
from sklearn.neighbors import KNeighborsClassifier
from sklearn.preprocessing import StandardScaler

from ml_utils import classification_metrics, print_metrics, split_dataset


def main() -> None:
    data = load_iris()
    split = split_dataset(data.data, data.target)

    scaler = StandardScaler()
    X_train = scaler.fit_transform(split.X_train)
    X_test = scaler.transform(split.X_test)

    model = KNeighborsClassifier(n_neighbors=5)
    model.fit(X_train, split.y_train)
    predictions = model.predict(X_test)
    metrics = classification_metrics(split.y_test, predictions)

    print("=" * 60)
    print("Chapter 36 — k-Nearest Neighbors")
    print("Dataset: Iris (sklearn)")
    print("=" * 60)
    print(f"k = {model.n_neighbors}")
    print_metrics("Test metrics", metrics)
    print("=" * 60)


if __name__ == "__main__":
    main()
