"""Governance curriculum evaluation tests."""

from app.services.governance_service import GovernanceService


class TestGovernanceCurriculum:
    def setup_method(self):
        self.service = GovernanceService()

    def test_curriculum_score_aligned(self):
        result = self.service.evaluate_curriculum_recommendation(
            curriculum_recommendation={
                "lesson_id": "grammar-9-modal-verbs",
                "title": "Modal Verbs",
                "skill_focus": "grammar",
                "reason": "Weakest skill is grammar.",
                "route": "/grammar-class",
            },
            weakest_skill="grammar",
        )
        assert result.score >= 0.8
        assert result.weakest_skill_match >= 0.9

    def test_curriculum_mismatch_warning(self):
        result = self.service.evaluate_curriculum_recommendation(
            curriculum_recommendation={
                "lesson_id": "speaking-restaurant",
                "skill_focus": "speaking",
                "title": "Restaurant",
                "route": "/conversation",
            },
            weakest_skill="grammar",
        )
        assert "curriculum_mismatch" in result.warnings

    def test_no_recommendation(self):
        result = self.service.evaluate_curriculum_recommendation()
        assert "no_curriculum_recommendation" in result.warnings
