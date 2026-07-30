"""Tests for curriculum revision scheduling."""

from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, patch
from uuid import uuid4

import pytest

from app.models.curriculum import LessonCompletion, RevisionSchedule
from app.schemas.memory_intelligence import MemoryBundle, LessonReflection
from app.models.memory import ErrorTracking
from app.services.curriculum_intelligence_service import CurriculumIntelligenceService


class TestCurriculumRevision:
    @pytest.mark.asyncio
    async def test_due_revision_recommendation(self):
        service = CurriculumIntelligenceService()
        mock_db = AsyncMock()
        lid = uuid4()
        tid = uuid4()
        due_item = RevisionSchedule(
            id=uuid4(),
            tenant_id=tid,
            learner_id=lid,
            lesson_id="grammar-9-modal-verbs",
            source_type="error_tracking",
            title="Revision: Modal Verbs",
            skill_focus="grammar",
            route="/grammar-class?grade=9&lesson_id=modal-verbs",
            due_at=datetime.now(timezone.utc) - timedelta(hours=1),
            status="scheduled",
            priority=2,
        )
        from app.schemas.student_intelligence import (
            StudentProfileResponse,
            StudentSkillsResponse,
            StudentSummaryResponse,
        )
        summary = StudentSummaryResponse(
            profile=StudentProfileResponse(user_id=uuid4(), cefr_level="B1", confidence_score=0.7),
            skills=StudentSkillsResponse(),
            has_data=True,
            weakest_skill="vocabulary",
        )

        with patch(
            "app.services.curriculum_intelligence_service.has_completed_assessment",
            new_callable=AsyncMock,
            return_value=True,
        ):
            with patch(
                "app.services.curriculum_intelligence_service.get_completed_lessons",
                new_callable=AsyncMock,
                return_value=[],
            ):
                with patch(
                    "app.services.curriculum_intelligence_service.get_due_revision_items",
                    new_callable=AsyncMock,
                    return_value=[due_item],
                ):
                    bundle = await service._build_recommendations_for_learner(
                        mock_db,
                        learner_id=lid,
                        tenant_id=tid,
                        summary=summary,
                    )
        assert bundle.metadata.get("rule") == "revision_due"
        assert bundle.primary.lesson_id == "grammar-9-modal-verbs"

    @pytest.mark.asyncio
    async def test_schedule_from_error_occurrence(self):
        service = CurriculumIntelligenceService()
        mock_db = AsyncMock()
        lid = uuid4()
        tid = uuid4()
        err = ErrorTracking(
            tenant_id=tid,
            learner_id=lid,
            error_category="grammar",
            error_type="grammar",
            error_text="I am go",
            occurrence_count=5,
        )

        with patch(
            "app.services.curriculum_intelligence_service.get_error_tracking_rows",
            new_callable=AsyncMock,
            return_value=[err],
        ):
            with patch(
                "app.services.curriculum_intelligence_service.get_completed_lessons",
                new_callable=AsyncMock,
                return_value=[],
            ):
                with patch(
                    "app.services.curriculum_intelligence_service.create_revision_item",
                    new_callable=AsyncMock,
                ) as create_mock:
                    count = await service.schedule_revisions_from_signals(
                        mock_db,
                        tenant_id=tid,
                        learner_id=lid,
                    )
                    assert count >= 1
                    create_mock.assert_awaited()

    @pytest.mark.asyncio
    async def test_schedule_from_lesson_score(self):
        service = CurriculumIntelligenceService()
        mock_db = AsyncMock()
        lid = uuid4()
        tid = uuid4()
        comp = LessonCompletion(
            tenant_id=tid,
            learner_id=lid,
            lesson_id="grammar-8-present-perfect",
            title="Present Perfect",
            skill_focus="grammar",
            route="/grammar-class",
            score=85,
            completed_at=datetime.now(timezone.utc),
        )

        with patch(
            "app.services.curriculum_intelligence_service.get_error_tracking_rows",
            new_callable=AsyncMock,
            return_value=[],
        ):
            with patch(
                "app.services.curriculum_intelligence_service.get_completed_lessons",
                new_callable=AsyncMock,
                return_value=[comp],
            ):
                with patch(
                    "app.services.curriculum_intelligence_service.create_revision_item",
                    new_callable=AsyncMock,
                ) as create_mock:
                    count = await service.schedule_revisions_from_signals(mock_db, tenant_id=tid, learner_id=lid)
                    assert count >= 1
                    create_mock.assert_awaited()

    @pytest.mark.asyncio
    async def test_schedule_from_reflection(self):
        service = CurriculumIntelligenceService()
        mock_db = AsyncMock()
        lid = uuid4()
        tid = uuid4()
        memory = MemoryBundle(
            lesson_reflections=[
                LessonReflection(content="Focus grammar", recommended_focus="grammar"),
            ],
        )

        with patch(
            "app.services.curriculum_intelligence_service.get_error_tracking_rows",
            new_callable=AsyncMock,
            return_value=[],
        ):
            with patch(
                "app.services.curriculum_intelligence_service.get_completed_lessons",
                new_callable=AsyncMock,
                return_value=[],
            ):
                with patch(
                    "app.services.curriculum_intelligence_service.create_revision_item",
                    new_callable=AsyncMock,
                ) as create_mock:
                    count = await service.schedule_revisions_from_signals(
                        mock_db,
                        tenant_id=tid,
                        learner_id=lid,
                        memory_bundle=memory,
                    )
                    assert count >= 1
                    create_mock.assert_awaited()
