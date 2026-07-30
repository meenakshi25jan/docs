"""Governance teacher response evaluation tests."""

from app.services.governance_service import GovernanceService


class TestGovernanceTeacherEvaluation:
    def setup_method(self):
        self.service = GovernanceService()

    def test_teacher_score_calculation(self):
        result = self.service.evaluate_teacher_response(
            response="Great job! Let's practice past simple. What did you do yesterday?",
            teacher_brain={
                "teaching_strategy": "explain_rule",
                "next_prompt": "Tell me about your weekend.",
            },
            intent="teaching",
            agent_output={"encouragement": "Great job!"},
        )
        assert result.score >= 0.7
        assert result.practice_prompt_quality >= 0.9

    def test_excessive_length_warning(self):
        long_response = "word " * 200
        result = self.service.evaluate_teacher_response(response=long_response)
        assert "excessive_response_length" in result.warnings

    def test_empty_response(self):
        result = self.service.evaluate_teacher_response(response="")
        assert result.score == 0.0
        assert "empty_response" in result.warnings
