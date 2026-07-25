#!/usr/bin/env python3
"""Chapter 42 — Principal Component Analysis on Digits dataset."""

from __future__ import annotations

from sklearn.datasets import load_digits
from sklearn.decomposition import PCA


def main() -> None:
    data = load_digits()
    n_components = 10
    model = PCA(n_components=n_components, random_state=42)
    reduced = model.fit_transform(data.data)
    explained = model.explained_variance_ratio_.sum()

    print("=" * 60)
    print("Chapter 42 — Principal Component Analysis")
    print("Dataset: Digits (sklearn)")
    print("=" * 60)
    print(f"Original dimensions: {data.data.shape[1]}")
    print(f"Reduced dimensions: {reduced.shape[1]}")
    print(f"Variance explained (top {n_components}): {explained:.4f}")
    print(f"First PC variance ratio: {model.explained_variance_ratio_[0]:.4f}")
    print("=" * 60)


if __name__ == "__main__":
    main()
