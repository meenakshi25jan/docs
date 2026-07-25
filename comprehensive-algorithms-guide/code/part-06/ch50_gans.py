"""Chapter 50 — Minimal GAN on 1D Gaussian mixture (NumPy)."""

from __future__ import annotations

import numpy as np

RNG = np.random.default_rng(42)


def sigmoid(x: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-np.clip(x, -20, 20)))


def real_samples(n: int) -> np.ndarray:
    return RNG.choice([-2.0, 2.0], size=(n, 1)) + RNG.normal(0, 0.2, size=(n, 1))


def train_gan(steps: int = 1200, lr: float = 0.05) -> tuple[float, float]:
    w_d = RNG.normal(0, 0.1, size=(1, 1))
    b_d = np.zeros(1)
    w_g = RNG.normal(0, 0.1, size=(1, 1))
    b_g = np.zeros(1)

    for _ in range(steps):
        real = real_samples(32)
        z = RNG.normal(size=(32, 1))
        fake = z * w_g + b_g

        d_real = sigmoid(real @ w_d + b_d)
        d_fake = sigmoid(fake @ w_d + b_d)

        # Discriminator gradients
        err_real = d_real - 1.0
        err_fake = d_fake
        w_d -= lr * (real.T @ err_real + fake.T @ err_fake) / 32
        b_d -= lr * (err_real.mean() + err_fake.mean())

        # Generator gradients
        z = RNG.normal(size=(32, 1))
        fake = z * w_g + b_g
        d_fake = sigmoid(fake @ w_d + b_d)
        gen_grad = (1.0 - d_fake)
        w_g += lr * (z.T @ gen_grad).mean(axis=1, keepdims=True).T / 32
        b_g += lr * gen_grad.mean()

    real_mean = float(real_samples(500).mean())
    fake_mean = float((RNG.normal(size=(500, 1)) * w_g + b_g).mean())
    return real_mean, fake_mean


def main() -> float:
    real_mean, fake_mean = train_gan()
    gap = abs(real_mean - fake_mean)
    print(f"Real mean: {real_mean:.3f}, Fake mean: {fake_mean:.3f}, gap: {gap:.3f}")
    print("SUCCESS: GAN training loop completed")
    return gap


if __name__ == "__main__":
    main()
