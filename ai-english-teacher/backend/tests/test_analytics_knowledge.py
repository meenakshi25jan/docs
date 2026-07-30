"""Knowledge analytics tests."""

from unittest.mock import AsyncMock, patch
from uuid import uuid4

import pytest

from app.services.analytics_service import AnalyticsService


class TestKnowledgeAnalyticsAggregation:
    @pytest.mark.asyncio
    async def test_fallback_count_and_sources(self):
        learner_id = uuid4()
        messages = [
            {
                "knowledge_grounding": {
                    "chunk_count": 2,
                    "sources": ["grammar_curriculum"],
                    "fallback_used": False,
                },
                "governance": {"grounding_score": 0.9},
            },
            {
                "knowledge_grounding": {
                    "chunk_count": 0,
                    "sources": ["keyword"],
                    "fallback_used": True,
                },
                "governance": {"grounding_score": 0.4},
            },
        ]
        with patch(
            "app.services.analytics_service.get_learner_by_user_id",
            new_callable=AsyncMock,
            return_value=type("L", (), {"id": learner_id})(),
        ), patch(
            "app.services.analytics_service.get_assistant_message_metadata",
            new_callable=AsyncMock,
            return_value=messages,
        ):
            service = AnalyticsService()
            result = await service.get_knowledge(AsyncMock(), uuid4())

        assert result.has_data
        assert result.grounding_count == 2
        assert result.fallback_usage_count == 1
        assert result.source_distribution["grammar_curriculum"] == 1
        assert result.source_distribution["keyword"] == 1
        assert result.avg_chunk_count == 1.0

    @pytest.mark.asyncio
    async def test_empty_knowledge_safe(self):
        learner_id = uuid4()
        with patch(
            "app.services.analytics_service.get_learner_by_user_id",
            new_callable=AsyncMock,
            return_value=type("L", (), {"id": learner_id})(),
        ), patch(
            "app.services.analytics_service.get_assistant_message_metadata",
            new_callable=AsyncMock,
            return_value=[],
        ):
            service = AnalyticsService()
            result = await service.get_knowledge(AsyncMock(), uuid4())
        assert not result.has_data
