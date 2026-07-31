#!/usr/bin/env python3
"""Chapter 41 — DBSCAN on synthetic moons dataset."""

from __future__ import annotations

from sklearn.cluster import DBSCAN
from sklearn.datasets import make_moons
from sklearn.metrics import adjusted_rand_score


def main() -> None:
    X, y = make_moons(n_samples=300, noise=0.08, random_state=42)
    model = DBSCAN(eps=0.15, min_samples=5)
    labels = model.fit_predict(X)
    n_clusters = len(set(labels)) - (1 if -1 in labels else 0)
    n_noise = int((labels == -1).sum())
    ari = adjusted_rand_score(y, labels)

    print("=" * 60)
    print("Chapter 41 — DBSCAN")
    print("Dataset: make_moons (sklearn synthetic)")
    print("=" * 60)
    print(f"Clusters found: {n_clusters}")
    print(f"Noise points: {n_noise}")
    print(f"Adjusted Rand Index: {ari:.4f}")
    print("=" * 60)


if __name__ == "__main__":
    main()
