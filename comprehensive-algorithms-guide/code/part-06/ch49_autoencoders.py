"""Chapter 49 — Linear autoencoder for 2D -> 1D -> 2D reconstruction."""

from __future__ import annotations

import numpy as np

RNG = np.random.default_rng(42)


def train_autoencoder(x: np.ndarray, latent: int = 1, lr: float = 0.05, epochs: int = 2000) -> tuple[np.ndarray, np.ndarray]:
    n, d = x.shape
    w_enc = RNG.normal(0, 0.1, (d, latent))
    w_dec = RNG.normal(0, 0.1, (latent, d))

    for _ in range(epochs):
        z = x @ w_enc
        x_hat = z @ w_dec
        error = x_hat - x
        loss_grad = 2 * error / n
        w_dec -= lr * z.T @ loss_grad
        w_enc -= lr * x.T @ (loss_grad @ w_dec.T)

    return w_enc, w_dec


def reconstruction_error(x: np.ndarray, w_enc: np.ndarray, w_dec: np.ndarray) -> float:
    x_hat = (x @ w_enc) @ w_dec
    return float(np.mean((x_hat - x) ** 2))


def main() -> float:
    x = RNG.normal(size=(100, 2))
    w_enc, w_dec = train_autoencoder(x)
    mse = reconstruction_error(x, w_enc, w_dec)
    print(f"Reconstruction MSE: {mse:.6f}")
    print("SUCCESS: Autoencoder trained")
    return mse


if __name__ == "__main__":
    main()
