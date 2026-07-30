"""pgvector fallback tests."""

from unittest.mock import AsyncMock, patch

import pytest

from app.services.knowledge_intelligence_service import KnowledgeIntelligenceService
from app.services.knowledge_store import retrieve_knowledge


class TestKnowledgePgvectorFallback:
    @pytest.mark.asyncio
    async def test_pgvector_fallback_safety(self):
        with patch(
            "app.services.embeddings.embed_text",
            new_callable=AsyncMock,
            return_value=None,
        ):
            chunks = await retrieve_knowledge("present perfect tense")
        assert chunks
        assert chunks[0]["method"] == "keyword"

    @pytest.mark.asyncio
    async def test_vector_search_failure_fallback(self):
        with patch(
            "app.services.embeddings.embed_text",
            new_callable=AsyncMock,
            return_value=[0.1] * 1536,
        ), patch(
            "app.core.database.get_session_factory",
            side_effect=RuntimeError("no db"),
        ):
            chunks = await retrieve_knowledge("restaurant conversation")
        assert chunks
        assert any(c["method"] == "keyword" for c in chunks)

    @pytest.mark.asyncio
    async def test_service_uses_keyword_when_rag_empty(self):
        service = KnowledgeIntelligenceService()
        with patch(
            "app.services.knowledge_intelligence_service.retrieve_knowledge",
            new_callable=AsyncMock,
            return_value=[],
        ):
            result = await service.build_lesson_context("grammar-8-present-perfect")
        assert result.grounding.compact_text
        assert "perfect" in result.grounding.compact_text.lower()
