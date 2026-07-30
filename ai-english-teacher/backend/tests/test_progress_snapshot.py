"""Tests for progress snapshot recording."""

from unittest.mock import AsyncMock, patch
from uuid import uuid4

import pytest

from app.scoring.engine import ProficiencyEstimate
from app.services.progress_snapshot_service import (
    record_from_assessment,
    record_from_lesson_scores,
    record_from_skill_map,
)


@pytest.fixture
def estimate():
    return ProficiencyEstimate(
        overall_score=75.0,
        cefr="B1",
        ielts=6.0,
        pte=50,
        confidence=0.8,
    )


class TestProgressSnapshotService:
    @pytest.mark.asyncio
    async def test_record_from_skill_map(self, estimate):
        db = AsyncMock()
        tenant_id = uuid4()
        learner_id = uuid4()

        with patch(
            "app.services.progress_snapshot_service.create_progress_snapshot",
            new_callable=AsyncMock,
        ) as mock_create:
            await record_from_skill_map(
                db,
                tenant_id=tenant_id,
                learner_id=learner_id,
                skill_scores={"grammar": 80.0, "vocabulary": 70.0},
                estimate=estimate,
            )
            mock_create.assert_called_once()
            call_kwargs = mock_create.call_args.kwargs
            assert call_kwargs["grammar_score"] == 80.0
            assert call_kwargs["cefr_estimate"] == "B1"

    @pytest.mark.asyncio
    async def test_record_from_lesson_scores(self, estimate):
        db = AsyncMock()
        tenant_id = uuid4()
        learner_id = uuid4()

        with patch(
            "app.services.progress_snapshot_service.create_progress_snapshot",
            new_callable=AsyncMock,
        ) as mock_create:
            await record_from_lesson_scores(
                db,
                tenant_id=tenant_id,
                learner_id=learner_id,
                scores={
                    "overall_speaking": 85,
                    "fluency": 80,
                    "grammar": 75,
                    "communication_effectiveness": 82,
                },
                estimate=estimate,
            )
            mock_create.assert_called_once()
            call_kwargs = mock_create.call_args.kwargs
            assert call_kwargs["speaking_score"] == 85

    @pytest.mark.asyncio
    async def test_record_from_assessment(self, estimate):
        db = AsyncMock()
        tenant_id = uuid4()
        learner_id = uuid4()

        with patch(
            "app.services.progress_snapshot_service.create_progress_snapshot",
            new_callable=AsyncMock,
        ) as mock_create:
            await record_from_assessment(
                db,
                tenant_id=tenant_id,
                learner_id=learner_id,
                skill_scores={"grammar": 72.0, "writing": 68.0},
                estimate=estimate,
            )
            mock_create.assert_called_once()
