"""Curriculum analytics tests."""

from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, patch
from uuid import uuid4

import pytest

from app.models.curriculum import LessonCompletion, RevisionSchedule
from app.services.analytics_service import AnalyticsService


class TestCurriculumAnalytics:
    @pytest.mark.asyncio
    async def test_completion_aggregation(self):
        learner_id = uuid4()
        now = datetime.now(timezone.utc)
        completions = [
            LessonCompletion(
                tenant_id=uuid4(),
                learner_id=learner_id,
                lesson_id="grammar-1",
                title="Grammar",
                skill_focus="grammar",
                route="/grammar-class",
                score=85,
                completed_at=now,
            ),
            LessonCompletion(
                tenant_id=uuid4(),
                learner_id=learner_id,
                lesson_id="speaking-1",
                title="Speaking",
                skill_focus="speaking",
                route="/conversation",
                score=78,
                completed_at=now - timedelta(days=3),
            ),
        ]
        with patch(
            "app.services.analytics_service.get_learner_by_user_id",
            new_callable=AsyncMock,
            return_value=type("L", (), {"id": learner_id})(),
        ), patch(
            "app.services.analytics_service.get_lesson_completions",
            new_callable=AsyncMock,
            return_value=completions,
        ), patch(
            "app.services.analytics_service.get_revision_schedule_rows",
            new_callable=AsyncMock,
            return_value=[],
        ), patch(
            "app.services.analytics_service.get_assistant_message_metadata",
            new_callable=AsyncMock,
            return_value=[],
        ):
            service = AnalyticsService()
            result = await service.get_curriculum(AsyncMock(), uuid4())
        assert result.has_data
        assert result.lessons_completed == 2
        assert result.skill_focus_distribution["grammar"] == 1
        assert result.skill_focus_distribution["speaking"] == 1

    @pytest.mark.asyncio
    async def test_revision_pending_aggregation(self):
        learner_id = uuid4()
        now = datetime.now(timezone.utc)
        revisions = [
            RevisionSchedule(
                tenant_id=uuid4(),
                learner_id=learner_id,
                lesson_id="rev-1",
                source_type="mistake",
                title="Revision",
                skill_focus="grammar",
                route="/grammar-class",
                due_at=now - timedelta(days=1),
                status="scheduled",
            ),
        ]
        with patch(
            "app.services.analytics_service.get_learner_by_user_id",
            new_callable=AsyncMock,
            return_value=type("L", (), {"id": learner_id})(),
        ), patch(
            "app.services.analytics_service.get_lesson_completions",
            new_callable=AsyncMock,
            return_value=[],
        ), patch(
            "app.services.analytics_service.get_revision_schedule_rows",
            new_callable=AsyncMock,
            return_value=revisions,
        ), patch(
            "app.services.analytics_service.get_assistant_message_metadata",
            new_callable=AsyncMock,
            return_value=[],
        ):
            service = AnalyticsService()
            result = await service.get_curriculum(AsyncMock(), uuid4())
        assert result.revision_pending == 1
        assert result.revision_overdue == 1
