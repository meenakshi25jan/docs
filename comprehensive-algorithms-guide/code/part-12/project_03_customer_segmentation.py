"""Project 03 — Customer segmentation with k-Means, hierarchical, DBSCAN."""

from __future__ import annotations

import numpy as np
from sklearn.cluster import AgglomerativeClustering, DBSCAN, KMeans
from sklearn.datasets import make_blobs
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler

RNG = np.random.default_rng(42)


def generate_customers(n: int = 300) -> np.ndarray:
    x, _ = make_blobs(n_samples=n, centers=4, cluster_std=0.8, random_state=42)
    return x


def run_kmeans(x: np.ndarray, k: int = 4) -> tuple[np.ndarray, float]:
    model = KMeans(n_clusters=k, random_state=42, n_init=10)
    labels = model.fit_predict(x)
    score = silhouette_score(x, labels)
    return labels, score


def run_hierarchical(x: np.ndarray, k: int = 4) -> tuple[np.ndarray, float]:
    model = AgglomerativeClustering(n_clusters=k)
    labels = model.fit_predict(x)
    score = silhouette_score(x, labels)
    return labels, score


def run_dbscan(x: np.ndarray, eps: float = 0.5, min_samples: int = 5) -> tuple[np.ndarray, float]:
    model = DBSCAN(eps=eps, min_samples=min_samples)
    labels = model.fit_predict(x)
    mask = labels >= 0
    if mask.sum() < 2 or len(set(labels[mask])) < 2:
        return labels, 0.0
    score = silhouette_score(x[mask], labels[mask])
    return labels, score


def main() -> int:
    raw = generate_customers()
    x = StandardScaler().fit_transform(raw)

    km_labels, km_score = run_kmeans(x)
    hc_labels, hc_score = run_hierarchical(x)
    db_labels, db_score = run_dbscan(x)

    print(f"k-Means:      k=4, silhouette={km_score:.3f}, clusters={len(set(km_labels))}")
    print(f"Hierarchical: k=4, silhouette={hc_score:.3f}, clusters={len(set(hc_labels))}")
    print(f"DBSCAN:       silhouette={db_score:.3f}, clusters={len(set(db_labels)) - (1 if -1 in db_labels else 0)}")
    print("SUCCESS: Customer segmentation completed")
    return len(set(km_labels))


if __name__ == "__main__":
    main()
