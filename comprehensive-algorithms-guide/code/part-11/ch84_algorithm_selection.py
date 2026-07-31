"""Chapter 84 — Algorithm selection decision helpers."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any


class ProblemType(str, Enum):
    SHORTEST_PATH_UNWEIGHTED = "shortest_path_unweighted"
    SHORTEST_PATH_WEIGHTED = "shortest_path_weighted"
    SHORTEST_PATH_HEURISTIC = "shortest_path_heuristic"
    CLUSTERING = "clustering"
    REGRESSION = "regression"
    TEXT_CLASSIFICATION = "text_classification"
    IMAGE_CLASSIFICATION = "image_classification"
    COMBINATORIAL_OPTIMIZATION = "combinatorial_optimization"
    REINFORCEMENT_LEARNING = "reinforcement_learning"


@dataclass(frozen=True)
class ProblemProfile:
    problem_type: ProblemType
    n_samples: int = 1000
    n_features: int = 10
    labeled: bool = True
    need_interpretability: bool = False
    latency_ms: float = 100.0
    has_heuristic: bool = False


RECOMMENDATIONS: dict[ProblemType, list[str]] = {
    ProblemType.SHORTEST_PATH_UNWEIGHTED: ["bfs"],
    ProblemType.SHORTEST_PATH_WEIGHTED: ["dijkstra"],
    ProblemType.SHORTEST_PATH_HEURISTIC: ["astar"],
    ProblemType.CLUSTERING: ["kmeans", "hierarchical", "dbscan"],
    ProblemType.REGRESSION: ["linear_regression", "random_forest", "xgboost", "lightgbm"],
    ProblemType.TEXT_CLASSIFICATION: ["naive_bayes", "logistic_regression", "svm", "tfidf_logistic"],
    ProblemType.IMAGE_CLASSIFICATION: ["cnn", "transfer_learning"],
    ProblemType.COMBINATORIAL_OPTIMIZATION: ["genetic_algorithm", "pso", "simulated_annealing", "differential_evolution"],
    ProblemType.REINFORCEMENT_LEARNING: ["q_learning", "dqn"],
}


def recommend(profile: ProblemProfile) -> str:
    """Return the primary recommended algorithm for a problem profile."""
    candidates = RECOMMENDATIONS[profile.problem_type]
    if profile.problem_type == ProblemType.CLUSTERING:
        if profile.n_samples > 50_000:
            return "kmeans"
        if profile.need_interpretability:
            return "hierarchical"
        return "dbscan" if profile.n_features > 20 else "kmeans"

    if profile.problem_type == ProblemType.REGRESSION:
        if profile.need_interpretability:
            return "linear_regression"
        if profile.n_samples > 100_000:
            return "lightgbm"
        return "random_forest" if profile.n_samples < 5000 else "xgboost"

    if profile.problem_type == ProblemType.TEXT_CLASSIFICATION:
        if profile.n_samples < 500:
            return "naive_bayes"
        if profile.latency_ms < 10:
            return "tfidf_logistic"
        return "svm"

    if profile.problem_type == ProblemType.IMAGE_CLASSIFICATION:
        return "transfer_learning" if profile.n_samples < 5000 else "cnn"

    if profile.problem_type == ProblemType.COMBINATORIAL_OPTIMIZATION:
        return "genetic_algorithm"

    if profile.problem_type == ProblemType.REINFORCEMENT_LEARNING:
        return "q_learning" if profile.n_features < 100 else "dqn"

    if profile.problem_type == ProblemType.SHORTEST_PATH_HEURISTIC and profile.has_heuristic:
        return "astar"
    if profile.problem_type == ProblemType.SHORTEST_PATH_WEIGHTED:
        return "dijkstra"
    return candidates[0]


def explain(profile: ProblemProfile) -> dict[str, Any]:
    """Return recommendation with rationale and alternates."""
    primary = recommend(profile)
    alternates = [a for a in RECOMMENDATIONS[profile.problem_type] if a != primary]
    return {
        "problem_type": profile.problem_type.value,
        "primary": primary,
        "alternates": alternates[:3],
        "profile": {
            "n_samples": profile.n_samples,
            "n_features": profile.n_features,
            "labeled": profile.labeled,
            "need_interpretability": profile.need_interpretability,
            "latency_ms": profile.latency_ms,
        },
    }


def main() -> str:
    examples = [
        ProblemProfile(ProblemType.SHORTEST_PATH_UNWEIGHTED),
        ProblemProfile(ProblemType.SHORTEST_PATH_WEIGHTED),
        ProblemProfile(ProblemType.SHORTEST_PATH_HEURISTIC, has_heuristic=True),
        ProblemProfile(ProblemType.CLUSTERING, n_samples=200),
        ProblemProfile(ProblemType.REGRESSION, need_interpretability=True),
        ProblemProfile(ProblemType.TEXT_CLASSIFICATION, n_samples=100),
        ProblemProfile(ProblemType.IMAGE_CLASSIFICATION, n_samples=1000),
        ProblemProfile(ProblemType.COMBINATORIAL_OPTIMIZATION),
        ProblemProfile(ProblemType.REINFORCEMENT_LEARNING, n_features=4),
    ]
    for ex in examples:
        result = explain(ex)
        print(f"{result['problem_type']:30s} -> {result['primary']}")
    choice = recommend(examples[0])
    print("SUCCESS: Algorithm selection guide ready")
    return choice


if __name__ == "__main__":
    main()
