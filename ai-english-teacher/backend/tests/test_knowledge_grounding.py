"""Tests for grounding context builder."""

from unittest.mock import AsyncMock, patch

import pytest

from app.services.knowledge_intelligence_service import KnowledgeIntelligenceService


class TestKnowledgeGrounding:
    @pytest.mark.asyncio
    async def test_grounding_context_compact(self):
        service = KnowledgeIntelligenceService()
        with patch(
            "app.services.knowledge_intelligence_service.retrieve_knowledge",
            new_callable=AsyncMock,
            return_value=[],
        ):
            grounding = await service.build_grounding_context(
                message="explain modal verbs",
                lesson_id="grammar-9-modal-verbs",
                cefr_level="B1",
            )
        assert grounding.compact_text
        assert grounding.validation.voice_ok

    def test_inject_teaching_instruction(self):
        service = KnowledgeIntelligenceService()
        from app.schemas.knowledge_intelligence import GroundingContext, GroundingValidation

        grounding = GroundingContext(
            compact_text="Use past simple for yesterday.",
            validation=GroundingValidation(),
        )
        result = service.inject_teaching_instruction("Correct gently.", grounding)
        assert "Teaching knowledge:" in result
        assert "past simple" in result.lower()

    def test_to_metadata(self):
        service = KnowledgeIntelligenceService()
        from app.schemas.knowledge_intelligence import GroundingContext, GroundingValidation

        grounding = GroundingContext(
            compact_text="test",
            lesson_id="grammar-9-modal-verbs",
            skill_focus="grammar",
            sources=["grammar_curriculum"],
            validation=GroundingValidation(chunk_count=1),
        )
        meta = service.to_metadata(grounding)
        assert meta.lesson_id == "grammar-9-modal-verbs"
        assert meta.chunk_count == 1
