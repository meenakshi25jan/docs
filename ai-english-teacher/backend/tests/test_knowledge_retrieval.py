"""Tests for knowledge retrieval."""

from unittest.mock import AsyncMock, patch

import pytest

from app.services.knowledge_intelligence_service import KnowledgeIntelligenceService


@pytest.fixture
def service():
    return KnowledgeIntelligenceService()


class TestKnowledgeRetrieval:
    @pytest.mark.asyncio
    async def test_lesson_context_generation(self, service):
        with patch(
            "app.services.knowledge_intelligence_service.retrieve_knowledge",
            new_callable=AsyncMock,
            return_value=[],
        ):
            result = await service.build_lesson_context("grammar-9-modal-verbs", cefr_level="B1")
        assert result.lesson_id == "grammar-9-modal-verbs"
        assert result.grounding.compact_text
        assert "can" in result.grounding.compact_text.lower() or "must" in result.grounding.compact_text.lower()

    @pytest.mark.asyncio
    async def test_mistake_context_generation(self, service):
        with patch(
            "app.services.knowledge_intelligence_service.retrieve_knowledge",
            new_callable=AsyncMock,
            return_value=[],
        ):
            result = await service.build_mistake_context("past_tense", cefr_level="B1")
        assert result.error_category == "past_tense"
        assert result.grounding.compact_text
        assert "past" in result.grounding.compact_text.lower()

    @pytest.mark.asyncio
    async def test_search_retrieval(self, service):
        with patch(
            "app.services.knowledge_intelligence_service.retrieve_knowledge",
            new_callable=AsyncMock,
            return_value=[
                {
                    "text": "Present perfect uses have/has + past participle.",
                    "source": "Grammar Unit 4",
                    "topic": "present perfect",
                    "score": 0.9,
                    "method": "keyword",
                }
            ],
        ):
            result = await service.search("present perfect tense")
        assert result.query == "present perfect tense"
        assert result.grounding.compact_text

    @pytest.mark.asyncio
    async def test_keyword_fallback_retrieval(self, service):
        with patch(
            "app.services.knowledge_intelligence_service.retrieve_knowledge",
            new_callable=AsyncMock,
            return_value=[],
        ):
            result = await service.search("explain present perfect tense")
        assert result.grounding.compact_text
        assert result.grounding.validation.fallback_used or result.chunks

    @pytest.mark.asyncio
    async def test_retrieval_failure_safety(self, service):
        with patch(
            "app.services.knowledge_intelligence_service.retrieve_knowledge",
            new_callable=AsyncMock,
            side_effect=RuntimeError("db down"),
        ):
            grounding = await service.build_grounding_context(message="hello", retrieve=True)
        assert grounding.validation.fallback_used or grounding.validation.retrieval_method == "error"
