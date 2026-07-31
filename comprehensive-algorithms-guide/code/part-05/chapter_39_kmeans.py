#!/usr/bin/env python3
"""Chapter 39 — k-Means clustering on Iris dataset."""

from __future__ import annotations

from sklearn.cluster import KMeans
from sklearn.datasets import load_iris
from sklearn.metrics import adjusted_rand_score


def main() -> None:
    data = load_iris()
    k = 3
    model = KMeans(n_clusters=k, random_state=42, n_init=10)
    labels = model.fit_predict(data.data)
    ari = adjusted_rand_score(data.target, labels)

    print("=" * 60)
    print("Chapter 39 — k-Means Clustering")
    print("Dataset: Iris (sklearn)")
    print("=" * 60)
    print(f"Clusters: {k}")
    print(f"Adjusted Rand Index vs true labels: {ari:.4f}")
    print("Centroids (first 2 features):")
    for i, center in enumerate(model.cluster_centers_):
        print(f"  Cluster {i}: [{center[0]:.2f}, {center[1]:.2f}, ...]")
    print("=" * 60)


if __name__ == "__main__":
    main()
