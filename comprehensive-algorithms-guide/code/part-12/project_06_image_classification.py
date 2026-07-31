"""Project 06 — Image classification with CNN and transfer-learning-style features."""

from __future__ import annotations

import numpy as np
from sklearn.datasets import load_digits
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
from sklearn.neural_network import MLPClassifier
from sklearn.preprocessing import StandardScaler

RNG = np.random.default_rng(42)


def relu(x: np.ndarray) -> np.ndarray:
    return np.maximum(0, x)


def max_pool2d(x: np.ndarray) -> np.ndarray:
    h, w = x.shape
    out = np.zeros((h // 2, w // 2))
    for i in range(0, h, 2):
        for j in range(0, w, 2):
            block = x[i : i + 2, j : j + 2]
            out[i // 2, j // 2] = block.max()
    return out


def conv2d_valid(img: np.ndarray, kernel: np.ndarray) -> np.ndarray:
    kh, kw = kernel.shape
    out_h = img.shape[0] - kh + 1
    out_w = img.shape[1] - kw + 1
    out = np.zeros((out_h, out_w))
    for i in range(out_h):
        for j in range(out_w):
            out[i, j] = float((img[i : i + kh, j : j + kw] * kernel).sum())
    return out


def cnn_features(images: np.ndarray) -> np.ndarray:
    """Minimal CNN feature extractor (NumPy) on 8x8 digit images."""
    kernel = np.array([[1, 0, -1], [1, 0, -1], [1, 0, -1]], dtype=float)
    feats: list[np.ndarray] = []
    for img in images:
        img2d = img.reshape(8, 8)
        conv = relu(conv2d_valid(img2d, kernel))
        pooled = max_pool2d(conv)
        feats.append(pooled.ravel())
    return np.array(feats)


def pretrained_features(images: np.ndarray) -> np.ndarray:
    """Transfer-learning-style: fixed random projection as pretrained backbone."""
    w = RNG.normal(0, 0.1, size=(64, 32))
    return np.tanh(images @ w)


def main() -> float:
    digits = load_digits()
    x = digits.data / 16.0
    y = digits.target
    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.2, random_state=42)

    cnn_clf = MLPClassifier(hidden_layer_sizes=(128, 64), max_iter=800, random_state=42)
    cnn_clf.fit(x_train, y_train)
    cnn_acc = float(accuracy_score(y_test, cnn_clf.predict(x_test)))

    tl_x_train = StandardScaler().fit_transform(pretrained_features(x_train))
    tl_x_test = StandardScaler().fit_transform(pretrained_features(x_test))
    tl_clf = LogisticRegression(max_iter=1000)
    tl_clf.fit(tl_x_train, y_train)
    tl_acc = float(accuracy_score(y_test, tl_clf.predict(tl_x_test)))

    conv_train = StandardScaler().fit_transform(cnn_features(x_train))
    conv_test = StandardScaler().fit_transform(cnn_features(x_test))
    conv_clf = LogisticRegression(max_iter=1000)
    conv_clf.fit(conv_train, y_train)
    conv_acc = float(accuracy_score(y_test, conv_clf.predict(conv_test)))

    print(f"CNN (MLP) accuracy:                {cnn_acc:.3f}")
    print(f"Conv features accuracy:            {conv_acc:.3f}")
    print(f"Transfer-learning features accuracy: {tl_acc:.3f}")
    print("SUCCESS: Image classification completed")
    return max(cnn_acc, conv_acc, tl_acc)


if __name__ == "__main__":
    main()
