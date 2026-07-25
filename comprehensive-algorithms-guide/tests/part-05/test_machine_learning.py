"""Tests for Part 5 — Machine Learning (Chapters 30-43)."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

CODE_DIR = Path(__file__).resolve().parents[2] / "code" / "part-05"

ML_SCRIPTS = [
    "chapter_30_linear_regression.py",
    "chapter_31_logistic_regression.py",
    "chapter_32_decision_tree.py",
    "chapter_33_random_forest.py",
    "chapter_34_naive_bayes.py",
    "chapter_35_svm.py",
    "chapter_36_knn.py",
    "chapter_37_xgboost.py",
    "chapter_38_lightgbm.py",
    "chapter_39_kmeans.py",
    "chapter_40_hierarchical_clustering.py",
    "chapter_41_dbscan.py",
    "chapter_42_pca.py",
    "chapter_43_apriori.py",
]


def _run_script(name: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(CODE_DIR / name)],
        capture_output=True,
        text=True,
        check=False,
    )


@pytest.mark.parametrize("script", ML_SCRIPTS)
def test_ml_scripts_exit_zero(script: str) -> None:
    result = _run_script(script)
    assert result.returncode == 0, result.stderr
    assert "=" * 60 in result.stdout


def test_linear_regression_r2_positive() -> None:
    from sklearn.datasets import fetch_california_housing
    from sklearn.linear_model import LinearRegression
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import r2_score

    data = fetch_california_housing()
    X_train, X_test, y_train, y_test = train_test_split(
        data.data, data.target, test_size=0.25, random_state=42
    )
    model = LinearRegression().fit(X_train, y_train)
    r2 = r2_score(y_test, model.predict(X_test))
    assert r2 > 0.5


def test_logistic_regression_accuracy() -> None:
    from sklearn.datasets import load_breast_cancer
    from sklearn.linear_model import LogisticRegression
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import accuracy_score

    data = load_breast_cancer()
    X_train, X_test, y_train, y_test = train_test_split(
        data.data, data.target, test_size=0.25, random_state=42
    )
    model = LogisticRegression(max_iter=1000).fit(X_train, y_train)
    acc = accuracy_score(y_test, model.predict(X_test))
    assert acc > 0.9


def test_apriori_finds_milk() -> None:
    from chapter_43_apriori import apriori, transactions_from_lists

    baskets = [
        ["milk", "bread"],
        ["milk", "bread", "butter"],
        ["beer", "diapers"],
        ["milk", "diapers"],
    ]
    frequent = apriori(transactions_from_lists(baskets), min_support=0.5)
    itemsets = [fs for fs, _ in frequent]
    assert frozenset({"milk"}) in itemsets


def test_pca_variance_explained() -> None:
    from sklearn.datasets import load_digits
    from sklearn.decomposition import PCA

    data = load_digits()
    model = PCA(n_components=10, random_state=42).fit(data.data)
    assert model.explained_variance_ratio_.sum() > 0.5


def test_dbscan_finds_two_clusters() -> None:
    from sklearn.cluster import DBSCAN
    from sklearn.datasets import make_moons

    X, _ = make_moons(n_samples=200, noise=0.05, random_state=42)
    labels = DBSCAN(eps=0.15, min_samples=5).fit_predict(X)
    n_clusters = len(set(labels)) - (1 if -1 in labels else 0)
    assert n_clusters == 2
