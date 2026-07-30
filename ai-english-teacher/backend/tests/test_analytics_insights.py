"""Learner insights tests."""

from unittest.mock import AsyncMock, patch
from uuid import uuid4

import pytest

from app.schemas.student_intelligence import (
    ProgressSnapshotSummary,
    SkillScoreDetail,
    StudentProfileResponse,
    StudentSkillsResponse,
    StudentSummaryResponse,
)
from app.services.analytics_service import AnalyticsService


class TestLearnerInsights:
    @pytest.mark.asyncio
    async def test_insight_for_weakest_skill(self):
        learner_id = uuid4()
        summary = StudentSummaryResponse(
            profile=StudentProfileResponse(user_id=uuid4(), cefr_level="B1"),
            skills=StudentSkillsResponse(
                grammar=SkillScoreDetail(score=50, trend="down"),
                speaking=SkillScoreDetail(score=80, trend="up"),
            ),
            top_mistakes=[],
            latest_progress=ProgressSnapshotSummary(cefr_estimate="B1"),
            strongest_skill="speaking",
            weakest_skill="grammar",
            recommended_next_focus="grammar class",
            has_data=True,
        )
        with patch(
            "app.services.analytics_service.get_learner_by_user_id",
            new_callable=AsyncMock,
            return_value=type("L", (), {"id": learner_id})(),
        ), patch(
            "app.services.analytics_service.get_summary",
            new_callable=AsyncMock,
            return_value=summary,
        ), patch(
            "app.services.analytics_service.get_error_tracking_rows",
            new_callable=AsyncMock,
            return_value=[],
        ), patch.object(
            AnalyticsService,
            "get_governance",
            new_callable=AsyncMock,
            return_value=type("G", (), {"warning_frequency": {}, "has_data": False})(),
        ), patch.object(
            AnalyticsService,
            "get_curriculum",
            new_callable=AsyncMock,
            return_value=type("C", (), {"revision_pending": 0, "lessons_completed_7d": 0, "has_data": False})(),
        ), patch.object(
            AnalyticsService,
            "get_progress",
            new_callable=AsyncMock,
            return_value=type("P", (), {"confidence_trend": None, "has_data": False})(),
        ):
            service = AnalyticsService()
            result = await service.get_insights(AsyncMock(), uuid4())

        assert result.has_data
        assert any(i.type == "weakness" and "grammar" in i.description.lower() for i in result.insights)

    @pytest.mark.asyncio
    async def test_insight_for_pending_revisions(self):
        learner_id = uuid4()
        summary = StudentSummaryResponse(
            profile=StudentProfileResponse(user_id=uuid4(), cefr_level="B1"),
            skills=StudentSkillsResponse(),
            top_mistakes=[],
            recommended_next_focus="practice",
            has_data=False,
        )
        with patch(
            "app.services.analytics_service.get_learner_by_user_id",
            new_callable=AsyncMock,
            return_value=type("L", (), {"id": learner_id})(),
        ), patch(
            "app.services.analytics_service.get_summary",
            new_callable=AsyncMock,
            return_value=summary,
        ), patch(
            "app.services.analytics_service.get_error_tracking_rows",
            new_callable=AsyncMock,
            return_value=[],
        ), patch.object(
            AnalyticsService,
            "get_governance",
            new_callable=AsyncMock,
            return_value=type("G", (), {"warning_frequency": {}, "has_data": False})(),
        ), patch.object(
            AnalyticsService,
            "get_curriculum",
            new_callable=AsyncMock,
            return_value=type("C", (), {"revision_pending": 2, "lessons_completed_7d": 0, "has_data": True})(),
        ), patch.object(
            AnalyticsService,
            "get_progress",
            new_callable=AsyncMock,
            return_value=type("P", (), {"confidence_trend": None, "has_data": False})(),
        ):
            service = AnalyticsService()
            result = await service.get_insights(AsyncMock(), uuid4())

        assert any(i.type == "curriculum" and "revision" in i.title.lower() for i in result.insights)
