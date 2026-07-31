"""Project 05 — Spam detection with Naive Bayes, logistic regression, SVM."""

from __future__ import annotations

import numpy as np
from sklearn.datasets import make_classification
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
from sklearn.svm import LinearSVC

RNG = np.random.default_rng(42)

SPAM_SAMPLES = [
    "win free money click now limited offer",
    "congratulations you won a prize claim today",
    "urgent act now exclusive deal guaranteed",
    "free gift card no cost verify account",
    "meeting tomorrow at three pm conference room",
    "project update attached please review feedback",
    "lunch schedule for next week team calendar",
    "quarterly report draft for your comments",
    "team offsite location confirmed for friday",
    "budget approval needed by end of week",
]


def generate_spam_corpus(n: int = 200) -> tuple[list[str], np.ndarray]:
    texts: list[str] = []
    labels: list[int] = []
    spam_words = ["free", "win", "click", "urgent", "prize", "guaranteed", "offer"]
    ham_words = ["meeting", "project", "report", "team", "schedule", "review", "budget"]

    for i in range(n):
        if i % 2 == 0:
            words = [RNG.choice(spam_words) for _ in range(8)]
            labels.append(1)
        else:
            words = [RNG.choice(ham_words) for _ in range(8)]
            labels.append(0)
        texts.append(" ".join(words))
    texts.extend(SPAM_SAMPLES)
    labels.extend([1, 1, 1, 1, 0, 0, 0, 0, 0, 0])
    return texts, np.array(labels)


def main() -> float:
    texts, y = generate_spam_corpus()
    x_train, x_test, y_train, y_test = train_test_split(texts, y, test_size=0.25, random_state=42)

    models = {
        "NaiveBayes": Pipeline([("vec", CountVectorizer()), ("clf", MultinomialNB())]),
        "LogisticRegression": Pipeline([("vec", CountVectorizer()), ("clf", LogisticRegression(max_iter=500))]),
        "LinearSVM": Pipeline([("vec", CountVectorizer()), ("clf", LinearSVC())]),
    }

    best_acc = 0.0
    for name, pipe in models.items():
        pipe.fit(x_train, y_train)
        preds = pipe.predict(x_test)
        acc = float(accuracy_score(y_test, preds))
        print(f"{name}: accuracy={acc:.3f}")
        best_acc = max(best_acc, acc)

    print(classification_report(y_test, models["LogisticRegression"].predict(x_test), target_names=["ham", "spam"]))
    print("SUCCESS: Spam detection completed")
    return best_acc


if __name__ == "__main__":
    main()
