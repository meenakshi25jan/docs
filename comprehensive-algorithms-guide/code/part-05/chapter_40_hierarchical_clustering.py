#!/usr/bin/env python3
"""Chapter 40 — Hierarchical Clustering on Wine dataset."""

from __future__ import annotations

from sklearn.cluster import AgglomerativeClustering
from sklearn.datasets import load_wine
from sklearn.metrics import adjusted_rand_score


def main() -> None:
    data = load_wine()
    n_clusters = 3
    model = AgglomerativeClustering(n_clusters=n_clusters, linkage="ward")
    labels = model.fit_predict(data.data)
    ari = adjusted_rand_score(data.target, labels)

    print("=" * 60)
    print("Chapter 40 — Hierarchical Clustering")
    print("Dataset: Wine (sklearn)")
    print("=" * 60)
    print(f"Linkage: ward, Clusters: {n_clusters}")
    print(f"Adjusted Rand Index: {ari:.4f}")
    print(f"Cluster sizes: {[int((labels == i).sum()) for i in range(n_clusters)]}")
    print("=" * 60)


if __name__ == "__main__":
    main()
