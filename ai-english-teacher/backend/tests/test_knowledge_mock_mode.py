"""Mock mode knowledge tests — no real AI."""

from unittest.mock import AsyncMock, patch

import pytest

from app.services.knowledge_intelligence_service import KnowledgeIntelligenceService


class TestKnowledgeMockMode:
    @pytest.mark.asyncio
    async def test_mock_mode_retrieval(self):
        service = KnowledgeIntelligenceService()
        with patch(
            "app.services.knowledge_intelligence_service.retrieve_knowledge",
            new_callable=AsyncMock,
            return_value=[],
        ), patch(
            "app.services.embeddings.embed_text",
            new_callable=AsyncMock,
            return_value=None,
        ):
            result = await service.search("present perfect")
        assert result.grounding.compact_text or result.chunks
        assert result.grounding.validation.retrieval_method in ("keyword", "none", "error") or result.grounding.validation.fallback_used

    @pytest.mark.asyncio
    async def test_build_grounding_without_embeddings(self):
        service = KnowledgeIntelligenceService()
        with patch(
            "app.services.knowledge_intelligence_service.retrieve_knowledge",
            new_callable=AsyncMock,
            return_value=[],
        ):
            grounding = await service.build_grounding_context(
                message="Can you explain articles?",
                cefr_level="A1",
            )
        assert grounding.validation.fallback_used or grounding.compact_text
