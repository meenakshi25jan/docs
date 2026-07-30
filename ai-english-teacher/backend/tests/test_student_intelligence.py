"""Tests for Student Intelligence v1 API and service."""

from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest
from httpx import AsyncClient

from app.models import LearnerProfile, ProgressSnapshot, User
from app.schemas.student_intelligence import SkillScoreDetail, StudentProfileUpdate, StudentSkillsResponse
from app.services.student_intelligence_service import (
    build_skills,
    get_mistakes,
    get_profile,
    get_summary,
    update_profile,
    _recommend_focus,
)


@pytest.fixture
def learner_id():
    return uuid4()


@pytest.fixture
def user_id():
    return uuid4()


@pytest.fixture
def tenant_id():
    return uuid4()


@pytest.fixture
def mock_learner(learner_id, user_id, tenant_id):
    profile = MagicMock(spec=LearnerProfile)
    profile.id = learner_id
    profile.user_id = user_id
    profile.tenant_id = tenant_id
    profile.current_cefr = "B1"
    profile.ielts_estimate = 6.0
    profile.pte_estimate = 50
    profile.target_exam = "ielts"
    profile.preferences = {"learning_goal": "Improve speaking"}
    profile.created_at = datetime.now(timezone.utc)
    return profile


@pytest.fixture
def sample_user(user_id, tenant_id):
    user = MagicMock(spec=User)
    user.id = user_id
    user.tenant_id = tenant_id
    user.first_name = "Test"
    user.last_name = "Student"
    user.email = "test@example.com"
    return user


class TestRecommendationLogic:
    def test_no_data_recommends_placement(self):
        skills = StudentSkillsResponse()
        assert _recommend_focus(skills, has_data=False) == "placement assessment"

    def test_lowest_grammar_recommends_grammar_class(self):
        skills = StudentSkillsResponse(
            grammar=SkillScoreDetail(score=40),
            vocabulary=SkillScoreDetail(score=80),
            pronunciation=SkillScoreDetail(score=75),
        )
        assert _recommend_focus(skills, has_data=True) == "grammar class"


class TestStudentIntelligenceService:
    @pytest.mark.asyncio
    async def test_get_profile(self, mock_learner, sample_user, user_id):
        db = AsyncMock()
        snapshot = MagicMock(spec=ProgressSnapshot)
        snapshot.confidence_score = 0.85
        snapshot.snapshot_at = datetime.now(timezone.utc)

        with patch(
            "app.services.student_intelligence_service.get_learner_with_user",
            return_value=(mock_learner, sample_user),
        ):
            with patch(
                "app.services.student_intelligence_service.get_latest_progress_snapshots",
                return_value=[snapshot],
            ):
                profile = await get_profile(db, user_id=user_id)
                assert profile.user_id == user_id
                assert profile.cefr_level == "B1"
                assert profile.learning_goal == "Improve speaking"
                assert profile.name == "Test Student"

    @pytest.mark.asyncio
    async def test_update_profile(self, mock_learner, sample_user, user_id):
        db = AsyncMock()
        db.flush = AsyncMock()

        with patch(
            "app.services.student_intelligence_service.get_learner_with_user",
            return_value=(mock_learner, sample_user),
        ):
            with patch(
                "app.services.student_intelligence_service.get_profile",
                new_callable=AsyncMock,
            ) as mock_get:
                mock_get.return_value = MagicMock()
                await update_profile(
                    db,
                    user_id=user_id,
                    updates=StudentProfileUpdate(learning_goal="Pass IELTS", daily_goal_minutes=30),
                )
                assert mock_learner.preferences.get("learning_goal") == "Pass IELTS"
                assert mock_learner.preferences.get("daily_goal_minutes") == 30

    @pytest.mark.asyncio
    async def test_build_skills_empty_defaults(self, learner_id):
        db = AsyncMock()
        with patch(
            "app.services.student_intelligence_service.get_latest_progress_snapshots",
            return_value=[],
        ):
            with patch(
                "app.services.student_intelligence_service.get_voice_analysis_averages",
                return_value={},
            ):
                with patch(
                    "app.services.student_intelligence_service.get_assessment_skill_scores",
                    return_value={},
                ):
                    skills = await build_skills(db, learner_id=learner_id)
                    assert skills.grammar.score == 0
                    assert skills.speaking.trend == "unknown"

    @pytest.mark.asyncio
    async def test_get_mistakes_empty(self, learner_id):
        db = AsyncMock()
        with patch(
            "app.services.student_intelligence_service.get_error_tracking_rows",
            return_value=[],
        ):
            result = await get_mistakes(db, learner_id=learner_id)
            assert result.total == 0
            assert result.mistakes == []

    @pytest.mark.asyncio
    async def test_get_summary_safe_defaults(self, mock_learner, sample_user, user_id, learner_id):
        from app.schemas.student_intelligence import StudentProfileResponse, StudentMistakesResponse

        db = AsyncMock()
        profile_resp = StudentProfileResponse(
            user_id=user_id,
            cefr_level="B1",
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        with patch(
            "app.services.student_intelligence_service.get_learner_with_user",
            return_value=(mock_learner, sample_user),
        ):
            with patch(
                "app.services.student_intelligence_service.get_profile",
                new_callable=AsyncMock,
                return_value=profile_resp,
            ):
                with patch(
                    "app.services.student_intelligence_service.build_skills",
                    new_callable=AsyncMock,
                    return_value=StudentSkillsResponse(),
                ):
                    with patch(
                        "app.services.student_intelligence_service.get_mistakes",
                        new_callable=AsyncMock,
                        return_value=StudentMistakesResponse(),
                    ):
                        with patch(
                            "app.services.student_intelligence_service.get_latest_progress_snapshots",
                            return_value=[],
                        ):
                            with patch(
                                "app.services.student_intelligence_service.get_progress_history_count",
                                return_value=0,
                            ):
                                with patch(
                                    "app.services.student_intelligence_service.get_voice_analysis_averages",
                                    return_value={},
                                ):
                                    with patch(
                                        "app.services.student_intelligence_service.get_assessment_skill_scores",
                                        return_value={},
                                    ):
                                        summary = await get_summary(db, user_id=user_id)
                                        assert summary.recommended_next_focus == "placement assessment"
                                        assert summary.has_data is False


class TestStudentIntelligenceAPI:
    @pytest.mark.asyncio
    async def test_get_profile_authenticated(self, client: AsyncClient, user_id):
        from app.schemas.student_intelligence import StudentProfileResponse

        with patch(
            "app.api.v1.student_intelligence.get_profile",
            new_callable=AsyncMock,
            return_value=StudentProfileResponse(
                user_id=user_id,
                name="Test Student",
                cefr_level="B1",
                ielts_estimate=6.0,
                pte_estimate=50,
                current_level="B1",
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc),
            ),
        ):
            res = await client.get("/api/v1/student-intelligence/profile")
            assert res.status_code == 200
            data = res.json()
            assert data["cefr_level"] == "B1"

    @pytest.mark.asyncio
    async def test_patch_profile(self, client: AsyncClient, user_id):
        from app.schemas.student_intelligence import StudentProfileResponse

        with patch(
            "app.api.v1.student_intelligence.update_profile",
            new_callable=AsyncMock,
            return_value=StudentProfileResponse(
                user_id=user_id,
                learning_goal="Pass IELTS",
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc),
            ),
        ):
            res = await client.patch(
                "/api/v1/student-intelligence/profile",
                json={"learning_goal": "Pass IELTS"},
            )
            assert res.status_code == 200
            assert res.json()["learning_goal"] == "Pass IELTS"

    @pytest.mark.asyncio
    async def test_get_skills(self, client: AsyncClient, learner_id):
        with patch(
            "app.api.v1.student_intelligence._learner_id_from_user",
            new_callable=AsyncMock,
            return_value=learner_id,
        ):
            with patch(
                "app.api.v1.student_intelligence.build_skills",
                new_callable=AsyncMock,
                return_value=StudentSkillsResponse(),
            ):
                res = await client.get("/api/v1/student-intelligence/skills")
                assert res.status_code == 200
                data = res.json()
                assert "grammar" in data
                assert "pronunciation" in data
                assert "fluency" in data

    @pytest.mark.asyncio
    async def test_get_mistakes(self, client: AsyncClient, learner_id):
        from app.schemas.student_intelligence import StudentMistakesResponse

        with patch(
            "app.api.v1.student_intelligence._learner_id_from_user",
            new_callable=AsyncMock,
            return_value=learner_id,
        ):
            with patch(
                "app.api.v1.student_intelligence.get_mistakes",
                new_callable=AsyncMock,
                return_value=StudentMistakesResponse(),
            ):
                res = await client.get("/api/v1/student-intelligence/mistakes")
                assert res.status_code == 200

    @pytest.mark.asyncio
    async def test_get_summary_recommended_focus(self, client: AsyncClient, user_id):
        from app.schemas.student_intelligence import StudentSummaryResponse, StudentProfileResponse

        summary = StudentSummaryResponse(
            profile=StudentProfileResponse(
                user_id=user_id,
                cefr_level="B1",
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc),
            ),
            skills=StudentSkillsResponse(),
            recommended_next_focus="grammar class",
            has_data=True,
        )
        with patch(
            "app.api.v1.student_intelligence.get_summary",
            new_callable=AsyncMock,
            return_value=summary,
        ):
            res = await client.get("/api/v1/student-intelligence/summary")
            assert res.status_code == 200
            assert res.json()["recommended_next_focus"] == "grammar class"

    @pytest.mark.asyncio
    async def test_unauthenticated_fails(self, public_client: AsyncClient):
        res = await public_client.get("/api/v1/student-intelligence/profile")
        assert res.status_code in (401, 403)
