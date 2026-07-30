"""Governance grounding evaluation tests."""

from app.services.governance_service import GovernanceService


class TestGovernanceGrounding:
    def setup_method(self):
        self.service = GovernanceService()

    def test_grounding_score_with_chunks(self):
        result = self.service.evaluate_grounding(
            knowledge_grounding={
                "chunk_count": 2,
                "sources": ["grammar_curriculum"],
                "fallback_used": False,
                "lesson_id": "grammar-9-modal-verbs",
            },
            intent="teaching",
            tools_invoked=["curriculum_knowledge_base"],
        )
        assert result.score >= 0.7
        assert result.grounding_present >= 0.9

    def test_ungrounded_teaching_warning(self):
        result = self.service.evaluate_grounding(
            knowledge_grounding={"chunk_count": 0, "sources": [], "fallback_used": False},
            intent="grammar_explain",
            tools_invoked=["curriculum_knowledge_base"],
        )
        assert "ungrounded_teaching" in result.warnings

    def test_fallback_warning(self):
        result = self.service.evaluate_grounding(
            knowledge_grounding={"chunk_count": 1, "sources": ["keyword"], "fallback_used": True},
            intent="teaching",
        )
        assert "grounding_fallback_used" in result.warnings
