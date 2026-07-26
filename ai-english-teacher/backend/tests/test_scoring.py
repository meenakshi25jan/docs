import pytest
from app.scoring.engine import (
    aggregate_scores,
    calculate_confidence_score,
    calculate_grammar_score,
    calculate_listening_score,
    calculate_reading_score,
    calculate_speaking_score,
    calculate_vocabulary_score,
    calculate_writing_score,
    score_to_cefr,
    score_to_ielts,
    score_to_pte,
    SkillScore,
)


class TestCEFRMapping:
    @pytest.mark.parametrize("score,expected", [
        (95, "C2"), (80, "C1"), (65, "B2"), (45, "B1"), (25, "A2"), (10, "A1"),
    ])
    def test_score_to_cefr(self, score, expected):
        assert score_to_cefr(score) == expected


class TestIELTSMapping:
    def test_high_score(self):
        assert score_to_ielts(95) == 9.0

    def test_mid_score(self):
        assert score_to_ielts(56) == 6.5

    def test_low_score(self):
        assert score_to_ielts(10) == 3.0


class TestPTEMapping:
    def test_high_score(self):
        assert score_to_pte(91) == 90

    def test_mid_score(self):
        assert score_to_pte(56) == 58


class TestGrammarScore:
    def test_perfect_score(self):
        score = calculate_grammar_score(100, 100, 0)
        assert score == 100.0

    def test_weighted_calculation(self):
        score = calculate_grammar_score(80, 70, 20)
        expected = 80 * 0.50 + 70 * 0.30 + 80 * 0.20
        assert score == round(expected, 2)


class TestVocabularyScore:
    def test_calculation(self):
        score = calculate_vocabulary_score(80, 70, 60)
        expected = 80 * 0.35 + 70 * 0.40 + 60 * 0.25
        assert score == round(expected, 2)


class TestWritingScore:
    def test_equal_weights(self):
        score = calculate_writing_score(80, 70, 60, 50)
        assert score == 65.0


class TestSpeakingScore:
    def test_calculation(self):
        score = calculate_speaking_score(80, 70, 60, 50)
        expected = 80 * 0.30 + 70 * 0.25 + 60 * 0.25 + 50 * 0.20
        assert score == round(expected, 2)


class TestReadingListening:
    def test_reading_perfect(self):
        assert calculate_reading_score(10, 10) == 100.0

    def test_listening_partial(self):
        assert calculate_listening_score(7, 10) == 70.0


class TestAggregateScores:
    def test_full_skills(self):
        skills = {
            "grammar": 78, "vocabulary": 72, "writing": 75,
            "reading": 80, "listening": 70, "speaking": 68,
        }
        result = aggregate_scores(skills)
        assert result.cefr in ("B1", "B2")
        assert 5.0 <= result.ielts <= 8.0
        assert 30 <= result.pte <= 80
        assert result.confidence > 0

    def test_empty_scores(self):
        result = aggregate_scores({})
        assert result.cefr == "A1"
        assert result.overall_score == 0.0


class TestConfidenceScore:
    def test_high_confidence(self):
        scores = [SkillScore("grammar", 75, 0.9) for _ in range(6)]
        confidence = calculate_confidence_score(scores, data_points=10, score_variance=10)
        assert confidence > 50

    def test_low_confidence(self):
        scores = [SkillScore("grammar", 50, 0.5)]
        confidence = calculate_confidence_score(scores, data_points=1, score_variance=200)
        assert confidence < 50
