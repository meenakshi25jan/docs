"""Chapter 45 — Tiny 2D convolution + pooling (NumPy)."""

from __future__ import annotations

import numpy as np

RNG = np.random.default_rng(42)


def conv2d(image: np.ndarray, kernel: np.ndarray) -> np.ndarray:
    kh, kw = kernel.shape
    out = np.zeros((image.shape[0] - kh + 1, image.shape[1] - kw + 1))
    for i in range(out.shape[0]):
        for j in range(out.shape[1]):
            out[i, j] = np.sum(image[i : i + kh, j : j + kw] * kernel)
    return out


def max_pool2d(x: np.ndarray, size: int = 2) -> np.ndarray:
    h, w = x.shape
    out = np.zeros((h // size, w // size))
    for i in range(out.shape[0]):
        for j in range(out.shape[1]):
            block = x[i * size : (i + 1) * size, j * size : (j + 1) * size]
            out[i, j] = np.max(block)
    return out


def edge_detect(image: np.ndarray) -> np.ndarray:
    sobel_x = np.array([[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]], dtype=float)
    return conv2d(image, sobel_x)


def main() -> float:
    image = RNG.integers(0, 256, size=(8, 8)).astype(float)
    edges = edge_detect(image)
    pooled = max_pool2d(np.abs(edges))
    energy = float(np.mean(pooled))
    print(f"Input shape: {image.shape}, pooled shape: {pooled.shape}")
    print(f"Pooled edge energy: {energy:.4f}")
    print("SUCCESS: CNN-style conv + max pool completed")
    return energy


if __name__ == "__main__":
    main()
