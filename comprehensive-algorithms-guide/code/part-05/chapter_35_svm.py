#!/usr/bin/env python3
"""Chapter 35 — Support Vector Machine on Breast Cancer dataset."""

from __future__ import annotations

from sklearn.datasets import load_breast_cancer
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC

from ml_utils import classification_metrics, print_metrics, split_dataset


def main() -> None:
    data = load_breast_cancer()
    split = split_dataset(data.data, data.target)

    scaler = StandardScaler()
    X_train = scaler.fit_transform(split.X_train)
    X_test = scaler.transform(split.X_test)

    model = SVC(kernel="rbf", C=1.0, random_state=42)
    model.fit(X_train, split.y_train)
    predictions = model.predict(X_test)
    metrics = classification_metrics(split.y_test, predictions)

    print("=" * 60)
    print("Chapter 35 — Support Vector Machine")
    print("Dataset: Breast Cancer Wisconsin (sklearn)")
    print("=" * 60)
    print(f"Support vectors: {model.n_support_.sum()}")
    print_metrics("Test metrics", metrics)
    print("=" * 60)


if __name__ == "__main__":
    main()
