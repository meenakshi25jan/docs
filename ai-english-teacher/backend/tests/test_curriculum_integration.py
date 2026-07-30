"""Integration tests for curriculum + voice turn metadata."""

from unittest.mock import AsyncMock, patch

import pytest
from httpx import AsyncClient


class TestCurriculumIntegration:
    @pytest.mark.asyncio
    async def test_voice_turn_includes_curriculum_metadata(self, client: AsyncClient, learner_id):
        mock_result = {
            "transcript": "Hello",
            "response": "Hi there!",
            "teaching_mode": "none",
            "corrections": [],
            "voice_scores": {"overall": 80},
            "estimates": {},
            "teacher_brain": {"intent": "greeting"},
            "memory": {"recurring_mistakes_count": 0, "reflections_available": False, "memory_summary_available": False},
            "curriculum_recommendation": {
                "lesson_id": "speaking-everyday",
                "title": "Everyday Conversation",
                "reason": "Practice speaking",
                "route": "/conversation?scenario=everyday",
                "skill_focus": "speaking",
            },
            "agent_output": {},
            "metadata": {},
        }
        with patch("app.api.v1.voice.run_voice_turn", return_value=mock_result):
            client.mock_db.scalar = AsyncMock(return_value=client.mock_learner)
            res = await client.post(
                "/api/v1/voice/turn",
                json={"transcript": "Hello"},
            )
            assert res.status_code == 200
            data = res.json()
            assert data["response"] == "Hi there!"
            assert data["curriculum_recommendation"]["lesson_id"] == "speaking-everyday"

    @pytest.mark.asyncio
    async def test_lesson_complete_stored_via_service(self):
        from app.services.curriculum_intelligence_service import CurriculumIntelligenceService

        service = CurriculumIntelligenceService()
        mock_db = AsyncMock()
        lid = __import__("uuid").uuid4()
        tid = __import__("uuid").uuid4()

        with patch(
            "app.services.curriculum_intelligence_service.mark_lesson_complete",
            new_callable=AsyncMock,
        ) as mark_mock:
            from app.models.curriculum import LessonCompletion
            from datetime import datetime, timezone

            row = LessonCompletion(
                id=__import__("uuid").uuid4(),
                tenant_id=tid,
                learner_id=lid,
                lesson_id="grammar-9-modal-verbs",
                title="Modal Verbs",
                skill_focus="grammar",
                route="/grammar-class",
                completed_at=datetime.now(timezone.utc),
            )
            mark_mock.return_value = row
            with patch.object(service, "schedule_revisions_from_signals", new_callable=AsyncMock, return_value=0):
                result = await service.complete_lesson(
                    mock_db,
                    tenant_id=tid,
                    learner_id=lid,
                    lesson_id="grammar-9-modal-verbs",
                    score=92,
                )
                assert result.lesson_id == "grammar-9-modal-verbs"
                mark_mock.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_no_real_ai_in_recommendation(self):
        from app.services.curriculum_intelligence_service import CurriculumIntelligenceService
        from app.schemas.student_intelligence import StudentProfileResponse, StudentSkillsResponse, StudentSummaryResponse
        from uuid import uuid4

        service = CurriculumIntelligenceService()
        mock_db = AsyncMock()
        summary = StudentSummaryResponse(
            profile=StudentProfileResponse(user_id=uuid4(), cefr_level="B1", confidence_score=0.8),
            skills=StudentSkillsResponse(),
            has_data=True,
            weakest_skill="grammar",
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
        assert bundle.primary.lesson_id
        assert bundle.primary.reason
