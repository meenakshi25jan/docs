"""Tests for curriculum recommendation engine."""

from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest

from app.models.memory import ErrorTracking
from app.schemas.memory_intelligence import MemoryBundle, RecurringMistake
from app.schemas.student_intelligence import (
    StudentProfileResponse,
    StudentSkillsResponse,
    StudentSummaryResponse,
)
from app.services.curriculum_intelligence_service import CurriculumIntelligenceService


def _summary(
    *,
    cefr: str = "B1",
    target_exam: str | None = None,
    confidence: float = 0.7,
    weakest: str = "grammar",
    has_data: bool = True,
) -> StudentSummaryResponse:
    return StudentSummaryResponse(
        profile=StudentProfileResponse(
            user_id=uuid4(),
            cefr_level=cefr,
            target_exam=target_exam,
            confidence_score=confidence,
        ),
        skills=StudentSkillsResponse(),
        has_data=has_data,
        weakest_skill=weakest,
        recommended_next_focus=weakest,
    )


class TestCurriculumRecommendation:
    @pytest.mark.asyncio
    async def test_no_assessment_placement(self):
        service = CurriculumIntelligenceService()
        mock_db = AsyncMock()
        lid = uuid4()
        tid = uuid4()
        summary = _summary()

        with patch(
            "app.services.curriculum_intelligence_service.has_completed_assessment",
            new_callable=AsyncMock,
            return_value=False,
        ):
            with patch(
                "app.services.curriculum_intelligence_service.get_completed_lessons",
                new_callable=AsyncMock,
                return_value=[],
            ):
                bundle = await service._build_recommendations_for_learner(
                    mock_db,
                    learner_id=lid,
                    tenant_id=tid,
                    summary=summary,
                )
        assert bundle.primary.lesson_id == "placement-assessment"
        assert bundle.metadata.get("rule") == "placement_assessment"

    @pytest.mark.asyncio
    async def test_weak_grammar_recommendation(self):
        service = CurriculumIntelligenceService()
        mock_db = AsyncMock()
        summary = _summary(weakest="grammar")

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
                        bundle = await service._build_recommendations_for_learner(
                            mock_db,
                            learner_id=uuid4(),
                            tenant_id=uuid4(),
                            summary=summary,
                        )
        assert bundle.primary.skill_focus == "grammar"
        assert bundle.metadata.get("rule") == "weak_grammar"

    @pytest.mark.asyncio
    async def test_weak_pronunciation(self):
        service = CurriculumIntelligenceService()
        mock_db = AsyncMock()
        summary = _summary(weakest="pronunciation")

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
                        bundle = await service._build_recommendations_for_learner(
                            mock_db,
                            learner_id=uuid4(),
                            tenant_id=uuid4(),
                            summary=summary,
                        )
        assert bundle.primary.lesson_id == "pronunciation-practice"

    @pytest.mark.asyncio
    async def test_weak_fluency_conversation(self):
        service = CurriculumIntelligenceService()
        mock_db = AsyncMock()
        summary = _summary(weakest="fluency")

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
                        bundle = await service._build_recommendations_for_learner(
                            mock_db,
                            learner_id=uuid4(),
                            tenant_id=uuid4(),
                            summary=summary,
                        )
        assert bundle.primary.skill_focus in ("fluency", "speaking")

    @pytest.mark.asyncio
    async def test_ielts_target(self):
        service = CurriculumIntelligenceService()
        mock_db = AsyncMock()
        summary = _summary(target_exam="ielts", weakest="vocabulary")

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
                        bundle = await service._build_recommendations_for_learner(
                            mock_db,
                            learner_id=uuid4(),
                            tenant_id=uuid4(),
                            summary=summary,
                        )
        assert bundle.primary.lesson_id == "exam-ielts-examiner"

    @pytest.mark.asyncio
    async def test_pte_target(self):
        service = CurriculumIntelligenceService()
        mock_db = AsyncMock()
        summary = _summary(target_exam="pte", weakest="vocabulary")

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
                        bundle = await service._build_recommendations_for_learner(
                            mock_db,
                            learner_id=uuid4(),
                            tenant_id=uuid4(),
                            summary=summary,
                        )
        assert bundle.primary.lesson_id == "exam-pte-coach"

    @pytest.mark.asyncio
    async def test_recurring_mistake_revision(self):
        service = CurriculumIntelligenceService()
        mock_db = AsyncMock()
        summary = _summary(weakest="vocabulary")
        memory = MemoryBundle(
            recurring_mistakes=[
                RecurringMistake(error="I go", correction="I went", category="grammar", count=4),
            ],
        )
        lid = uuid4()
        err = ErrorTracking(
            tenant_id=uuid4(),
            learner_id=lid,
            error_category="grammar",
            error_type="grammar",
            error_text="I go",
            occurrence_count=1,
        )

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
                        bundle = await service._build_recommendations_for_learner(
                            mock_db,
                            learner_id=lid,
                            tenant_id=uuid4(),
                            summary=summary,
                            memory_bundle=memory,
                        )
        assert bundle.metadata.get("rule") == "recurring_mistake"
