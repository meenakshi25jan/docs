"""Tests for curriculum learning paths."""

from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest

from app.services.curriculum_intelligence_service import CurriculumIntelligenceService


class TestCurriculumPaths:
    @pytest.mark.asyncio
    async def test_daily_path_generated(self):
        service = CurriculumIntelligenceService()
        mock_db = AsyncMock()
        uid = uuid4()
        learner = MagicMock()
        learner.id = uuid4()
        learner.tenant_id = uuid4()
        learner.user_id = uid

        with patch(
            "app.repositories.student_intelligence_repository.get_learner_with_user",
            new_callable=AsyncMock,
            return_value=(learner, None),
        ):
            with patch(
                "app.services.curriculum_intelligence_service.get_summary",
                new_callable=AsyncMock,
            ):
                with patch(
                    "app.services.curriculum_intelligence_service.get_due_revision_items",
                    new_callable=AsyncMock,
                    return_value=[],
                ):
                    with patch.object(
                        service,
                        "build_recommendations",
                        new_callable=AsyncMock,
                    ) as rec_mock:
                        from app.schemas.curriculum_intelligence import (
                            CurriculumRecommendationBundle,
                            LessonRecommendationResponse,
                        )
                        rec_mock.return_value = CurriculumRecommendationBundle(
                            primary=LessonRecommendationResponse(
                                lesson_id="grammar-9-modal-verbs",
                                title="Modal Verbs",
                                reason="test",
                                route="/grammar-class",
                                skill_focus="grammar",
                            ),
                        )
                        path = await service.build_learning_path(mock_db, user_id=uid, path_type="daily")
        assert path.path_id == "daily"
        assert len(path.items) >= 1

    @pytest.mark.asyncio
    async def test_weekly_path_generated(self):
        service = CurriculumIntelligenceService()
        mock_db = AsyncMock()
        uid = uuid4()
        learner = MagicMock()
        learner.id = uuid4()

        with patch(
            "app.repositories.student_intelligence_repository.get_learner_with_user",
            new_callable=AsyncMock,
            return_value=(learner, None),
        ):
            with patch.object(service, "build_recommendations", new_callable=AsyncMock):
                with patch(
                    "app.services.curriculum_intelligence_service.has_completed_assessment",
                    new_callable=AsyncMock,
                    return_value=True,
                ):
                    with patch(
                        "app.services.curriculum_intelligence_service.get_due_revision_items",
                        new_callable=AsyncMock,
                        return_value=[],
                    ):
                        path = await service.build_learning_path(mock_db, user_id=uid, path_type="weekly")
        assert path.path_id == "weekly"
        assert len(path.items) >= 3

    @pytest.mark.asyncio
    async def test_exam_path_generated(self):
        service = CurriculumIntelligenceService()
        mock_db = AsyncMock()
        uid = uuid4()
        learner = MagicMock()
        learner.id = uuid4()

        with patch(
            "app.repositories.student_intelligence_repository.get_learner_with_user",
            new_callable=AsyncMock,
            return_value=(learner, None),
        ):
            with patch.object(service, "build_recommendations", new_callable=AsyncMock):
                path = await service.build_learning_path(mock_db, user_id=uid, path_type="exam")
        assert path.path_id == "exam"
        assert any("exam" in i.lesson_id for i in path.items)
