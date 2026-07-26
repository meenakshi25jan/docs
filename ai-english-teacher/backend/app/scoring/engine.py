"""
AI Scoring Engine

Calculates skill scores, CEFR estimates, IELTS bands, and PTE scores
using weighted formulas calibrated against standard proficiency frameworks.
"""

from dataclasses import dataclass
from typing import Literal

SkillName = Literal["grammar", "vocabulary", "writing", "reading", "listening", "speaking"]

CEFR_THRESHOLDS = [
    (91, "C2"), (76, "C1"), (56, "B2"), (36, "B1"), (21, "A2"), (0, "A1"),
]

IELTS_MAPPING = [
    (91, 9.0), (86, 8.5), (76, 8.0), (71, 7.5), (61, 7.0),
    (56, 6.5), (46, 6.0), (41, 5.5), (31, 5.0), (26, 4.5),
    (16, 4.0), (11, 3.5), (6, 3.0), (0, 2.5),
]

PTE_MAPPING = [
    (91, 90), (86, 85), (81, 80), (76, 76), (71, 72), (66, 68),
    (61, 64), (56, 58), (51, 54), (46, 50), (41, 46), (36, 42),
    (31, 38), (26, 34), (21, 30), (16, 26), (11, 22), (6, 18), (0, 10),
]

SKILL_WEIGHTS: dict[str, float] = {
    "grammar": 0.20,
    "vocabulary": 0.15,
    "writing": 0.20,
    "reading": 0.15,
    "listening": 0.15,
    "speaking": 0.15,
}


@dataclass
class SkillScore:
    skill: str
    score: float
    confidence: float
    dimension_scores: dict[str, float] | None = None


@dataclass
class ProficiencyEstimate:
    cefr: str
    ielts: float
    pte: int
    confidence: float
    overall_score: float


def score_to_cefr(score: float) -> str:
    for threshold, level in CEFR_THRESHOLDS:
        if score >= threshold:
            return level
    return "A1"


def score_to_ielts(score: float) -> float:
    for threshold, band in IELTS_MAPPING:
        if score >= threshold:
            return band
    return 2.5


def score_to_pte(score: float) -> int:
    for threshold, pte in PTE_MAPPING:
        if score >= threshold:
            return pte
    return 10


def calculate_grammar_score(
    accuracy: float,
    complexity: float,
    error_density: float,
) -> float:
    """
    Grammar Score = (Accuracy × 0.50) + (Complexity × 0.30) + ((1 - ErrorDensity) × 0.20)
    All inputs normalized 0-100.
    """
    error_penalty = max(0, 100 - error_density)
    return round(accuracy * 0.50 + complexity * 0.30 + error_penalty * 0.20, 2)


def calculate_vocabulary_score(
    range_score: float,
    accuracy: float,
    sophistication: float,
) -> float:
    """Vocabulary Score = (Range × 0.35) + (Accuracy × 0.40) + (Sophistication × 0.25)"""
    return round(range_score * 0.35 + accuracy * 0.40 + sophistication * 0.25, 2)


def calculate_writing_score(
    task_achievement: float,
    coherence: float,
    lexical_resource: float,
    grammatical_range: float,
) -> float:
    """IELTS Writing rubric: equal 25% weight per criterion."""
    return round(
        task_achievement * 0.25 + coherence * 0.25 + lexical_resource * 0.25 + grammatical_range * 0.25,
        2,
    )


def calculate_speaking_score(
    pronunciation: float,
    fluency: float,
    grammar: float,
    vocabulary: float,
) -> float:
    """Speaking Score = Pronunciation(30%) + Fluency(25%) + Grammar(25%) + Vocabulary(20%)"""
    return round(
        pronunciation * 0.30 + fluency * 0.25 + grammar * 0.25 + vocabulary * 0.20,
        2,
    )


def calculate_reading_score(correct: int, total: int, difficulty_factor: float = 1.0) -> float:
    """Reading Score = (Correct/Total × 100) × DifficultyFactor"""
    if total == 0:
        return 0.0
    base = (correct / total) * 100
    return round(min(100, base * difficulty_factor), 2)


def calculate_listening_score(correct: int, total: int, difficulty_factor: float = 1.0) -> float:
    return calculate_reading_score(correct, total, difficulty_factor)


def calculate_confidence_score(
    skill_scores: list[SkillScore],
    data_points: int,
    score_variance: float,
) -> float:
    """
    Confidence = (DataVolume × 0.40) + (Consistency × 0.35) + (SkillCoverage × 0.25)
    DataVolume: min(data_points / 10, 1.0)
    Consistency: max(0, 1 - variance/400)
    SkillCoverage: skills_assessed / 6
    """
    data_volume = min(data_points / 10, 1.0)
    consistency = max(0, 1 - score_variance / 400)
    coverage = len(skill_scores) / 6
    return round((data_volume * 0.40 + consistency * 0.35 + coverage * 0.25) * 100, 2)


def aggregate_scores(skill_scores: dict[str, float]) -> ProficiencyEstimate:
    """Aggregate per-skill scores into overall proficiency estimate."""
    if not skill_scores:
        return ProficiencyEstimate("A1", 2.5, 10, 0.0, 0.0)

    weighted_sum = 0.0
    weight_total = 0.0
    for skill, score in skill_scores.items():
        weight = SKILL_WEIGHTS.get(skill, 0.1)
        weighted_sum += score * weight
        weight_total += weight

    overall = round(weighted_sum / weight_total if weight_total > 0 else 0, 2)
    scores_list = list(skill_scores.values())
    variance = sum((s - overall) ** 2 for s in scores_list) / len(scores_list) if scores_list else 0

    confidence = calculate_confidence_score(
        [SkillScore(s, v, 0.8) for s, v in skill_scores.items()],
        data_points=len(scores_list),
        score_variance=variance,
    )

    return ProficiencyEstimate(
        cefr=score_to_cefr(overall),
        ielts=score_to_ielts(overall),
        pte=score_to_pte(overall),
        confidence=confidence,
        overall_score=overall,
    )
