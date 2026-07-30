"""Tests for knowledge ranking."""

from unittest.mock import AsyncMock, patch

import pytest

from app.services.knowledge_intelligence_service import KnowledgeIntelligenceService, _rank_chunks


class TestKnowledgeRanking:
    def test_ranking_lesson_priority(self):
        candidates = [
            {
                "text": "Generic speaking tip.",
                "source": "keyword",
                "topic": "speaking",
                "score": 0.9,
                "source_type": "keyword",
                "method": "keyword",
            },
            {
                "text": "Modal verbs express ability and obligation.",
                "source": "Grammar Grade 9",
                "topic": "grammar-9-modal-verbs",
                "score": 0.7,
                "source_type": "grammar_curriculum",
                "method": "grammar_curriculum",
                "lesson_match": True,
                "concept_match": True,
            },
        ]
        ranked = _rank_chunks(candidates, lesson_id="grammar-9-modal-verbs", cefr_level="B1")
        assert ranked[0]["source_type"] == "grammar_curriculum"

    def test_ranking_mistake_priority(self):
        candidates = [
            {
                "text": "Articles a an the.",
                "source": "keyword",
                "topic": "articles",
                "score": 0.8,
                "source_type": "keyword",
                "mistake_match": False,
            },
            {
                "text": "Use past simple for completed actions.",
                "source": "Mistake: past_tense",
                "topic": "past_tense",
                "score": 0.85,
                "source_type": "grammar_curriculum",
                "mistake_match": True,
            },
        ]
        ranked = _rank_chunks(candidates, mistake_categories=["past_tense"])
        assert ranked[0].get("mistake_match") is True

    @pytest.mark.asyncio
    async def test_cefr_filtering_in_search(self):
        service = KnowledgeIntelligenceService()
        with patch(
            "app.services.knowledge_intelligence_service.retrieve_knowledge",
            new_callable=AsyncMock,
            return_value=[],
        ):
            result = await service.build_lesson_context("grammar-5-articles", cefr_level="A1")
        assert result.grounding.cefr_level == "A1" or result.grounding.compact_text
