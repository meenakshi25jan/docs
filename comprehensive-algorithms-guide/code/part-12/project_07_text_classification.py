"""Project 07 — Text classification with TF-IDF and transformer-style embeddings."""

from __future__ import annotations

import numpy as np
from sklearn.datasets import fetch_20newsgroups
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split

RNG = np.random.default_rng(42)


def simple_token_embed(texts: list[str], dim: int = 32) -> np.ndarray:
    """Transformer-style bag-of-embeddings using hashed token vectors."""
    vocab_size = 2048
    table = RNG.normal(0, 0.05, size=(vocab_size, dim))
    out = np.zeros((len(texts), dim))
    for i, text in enumerate(texts):
        tokens = text.lower().split()
        if not tokens:
            continue
        vecs = []
        for tok in tokens:
            idx = hash(tok) % vocab_size
            vecs.append(table[idx])
        out[i] = np.mean(vecs, axis=0)
    return out


def load_subset() -> tuple[list[str], np.ndarray]:
    categories = ["sci.space", "rec.sport.baseball"]
    data = fetch_20newsgroups(subset="train", categories=categories, remove=("headers", "footers", "quotes"))
    texts = data.data[:400]
    labels = np.array(data.target[:400])
    return texts, labels


def main() -> float:
    texts, y = load_subset()
    x_train, x_test, y_train, y_test = train_test_split(texts, y, test_size=0.25, random_state=42)

    tfidf = TfidfVectorizer(max_features=2000, stop_words="english")
    x_train_tfidf = tfidf.fit_transform(x_train)
    x_test_tfidf = tfidf.transform(x_test)
    tfidf_clf = LogisticRegression(max_iter=500)
    tfidf_clf.fit(x_train_tfidf, y_train)
    tfidf_acc = float(accuracy_score(y_test, tfidf_clf.predict(x_test_tfidf)))

    x_train_emb = simple_token_embed(x_train)
    x_test_emb = simple_token_embed(x_test)
    emb_clf = LogisticRegression(max_iter=500)
    emb_clf.fit(x_train_emb, y_train)
    emb_acc = float(accuracy_score(y_test, emb_clf.predict(x_test_emb)))

    print(f"TF-IDF + Logistic accuracy:        {tfidf_acc:.3f}")
    print(f"Embedding + Logistic accuracy:     {emb_acc:.3f}")
    print("SUCCESS: Text classification completed")
    return max(tfidf_acc, emb_acc)


if __name__ == "__main__":
    main()
