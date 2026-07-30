"""API tests for Curriculum Intelligence."""

from unittest.mock import AsyncMock, patch
from uuid import uuid4

import pytest
from httpx import AsyncClient

from app.schemas.curriculum_intelligence import (
    CurriculumRecommendationBundle,
    LessonCompletionResponse,
    LessonRecommendationResponse,
    RevisionItemResponse,
)


class TestApiCurriculum:
    @pytest.mark.asyncio
    async def test_topics_public(self, public_client: AsyncClient):
        res = await public_client.get("/api/v1/curriculum/topics")
        assert res.status_code == 200
        data = res.json()
        assert len(data) >= 8

    @pytest.mark.asyncio
    async def test_recommended_authenticated(self, client: AsyncClient, learner_id):
        mock_bundle = CurriculumRecommendationBundle(
            primary=LessonRecommendationResponse(
                lesson_id="placement-assessment",
                title="Placement Assessment",
                reason="Start here",
                route="/assessment",
                skill_focus="general",
            ),
        )
        with patch(
            "app.services.curriculum_intelligence_service.CurriculumIntelligenceService.build_recommendations",
            new_callable=AsyncMock,
            return_value=mock_bundle,
        ):
            with patch(
                "app.services.memory_intelligence_service.MemoryIntelligenceService.build_bundle",
                new_callable=AsyncMock,
            ):
                client.mock_db.scalar = AsyncMock(return_value=client.mock_learner)
                res = await client.get("/api/v1/curriculum/recommended")
                assert res.status_code == 200
                assert res.json()["primary"]["lesson_id"] == "placement-assessment"

    @pytest.mark.asyncio
    async def test_lesson_complete(self, client: AsyncClient, learner_id):
        mock_resp = LessonCompletionResponse(
            id=str(uuid4()),
            lesson_id="speaking-everyday",
            title="Everyday Conversation",
            skill_focus="speaking",
            route="/conversation?scenario=everyday",
            score=88.0,
            completed_at="2026-01-01T00:00:00Z",
        )
        with patch(
            "app.services.curriculum_intelligence_service.CurriculumIntelligenceService.complete_lesson",
            new_callable=AsyncMock,
            return_value=mock_resp,
        ):
            client.mock_db.scalar = AsyncMock(return_value=client.mock_learner)
            res = await client.post(
                "/api/v1/curriculum/lesson-complete",
                json={"lesson_id": "speaking-everyday", "score": 88},
            )
            assert res.status_code == 200
            assert res.json()["lesson_id"] == "speaking-everyday"

    @pytest.mark.asyncio
    async def test_revision_schedule(self, client: AsyncClient, learner_id):
        with patch(
            "app.services.curriculum_intelligence_service.CurriculumIntelligenceService.list_revision_schedule",
            new_callable=AsyncMock,
            return_value=[
                RevisionItemResponse(
                    id=str(uuid4()),
                    lesson_id="grammar-9-modal-verbs",
                    title="Revision",
                    route="/grammar-class",
                    skill_focus="grammar",
                ),
            ],
        ):
            client.mock_db.scalar = AsyncMock(return_value=client.mock_learner)
            res = await client.get("/api/v1/curriculum/revision-schedule")
            assert res.status_code == 200
            assert len(res.json()) == 1

    @pytest.mark.asyncio
    async def test_learning_path_daily(self, client: AsyncClient, learner_id):
        from app.schemas.curriculum_intelligence import LearningPathResponse

        with patch(
            "app.services.curriculum_intelligence_service.CurriculumIntelligenceService.build_learning_path",
            new_callable=AsyncMock,
            return_value=LearningPathResponse(
                path_id="daily",
                title="Daily",
                description="Daily path",
                items=[],
            ),
        ):
            client.mock_db.scalar = AsyncMock(return_value=client.mock_learner)
            res = await client.get("/api/v1/curriculum/learning-path?type=daily")
            assert res.status_code == 200
            assert res.json()["path_id"] == "daily"
