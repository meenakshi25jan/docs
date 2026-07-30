"""Governance memory evaluation tests."""

from app.services.governance_service import GovernanceService


class TestGovernanceMemory:
    def setup_method(self):
        self.service = GovernanceService()

    def test_memory_score_full_context(self):
        result = self.service.evaluate_memory_usage(
            memory_meta={
                "recurring_mistakes_count": 2,
                "reflections_available": True,
                "memory_summary_available": True,
            },
        )
        assert result.score >= 0.8

    def test_missing_memory_context_warning(self):
        result = self.service.evaluate_memory_usage(
            memory_meta={
                "recurring_mistakes_count": 3,
                "reflections_available": False,
                "memory_summary_available": False,
            },
        )
        assert "missing_memory_context" in result.warnings

    def test_student_outcome_scoring(self):
        result = self.service.evaluate_student_outcome(
            strongest_skill="vocabulary",
            weakest_skill="grammar",
            confidence_score=0.7,
            skill_trends={"grammar": "up", "speaking": "stable"},
            has_data=True,
            lesson_completions_count=2,
        )
        assert result.score >= 0.6
