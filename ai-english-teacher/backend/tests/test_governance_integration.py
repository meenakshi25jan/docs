"""Governance integration tests."""

from unittest.mock import AsyncMock, patch

import pytest

from app.services.governance_service import GovernanceService


class TestGovernanceIntegration:
    @pytest.mark.asyncio
    async def test_voice_turn_governance_metadata(self, client, learner_id):
        with patch(
            "app.orchestration.voice.voice_turn.run_voice_analysis",
            new_callable=AsyncMock,
            return_value={
                "transcript": "I am go to market yesterday.",
                "fluency": 70,
                "pronunciation": 72,
                "grammar_score": 65,
                "vocabulary_score": 70,
                "overall_score": 68,
                "details": {"grammar": {"errors": []}},
            },
        ), patch(
            "app.orchestration.runner.run_conversation_turn",
            new_callable=AsyncMock,
            return_value=type(
                "O",
                (),
                {
                    "data": {"response": "Use past simple: I went to the market."},
                    "metadata": {"intent": "teaching", "trace_id": "trace-1"},
                },
            )(),
        ):
            from app.orchestration.voice.voice_turn import run_voice_turn

            result = await run_voice_turn(
                session_id="sess-gov",
                learner_id=str(learner_id),
                tenant_id=None,
                scenario="everyday",
                cefr_level="B1",
                message_history=[],
                transcript="I am go to market yesterday.",
            )
        assert result.get("response")
        assert result.get("governance") is not None
        assert "teacher_response_score" in result["governance"]

    def test_safe_failure_path(self):
        service = GovernanceService()
        result = service.evaluate_turn(
            learner_id="learner-1",
            response="Hello",
            store=True,
        )
        assert result.governance.overall_score >= 0

    @pytest.mark.asyncio
    async def test_evaluate_turn_safe_returns_none_on_error(self):
        service = GovernanceService()
        with patch.object(service, "evaluate_turn", side_effect=RuntimeError("fail")):
            out = await service.evaluate_turn_safe(learner_id="x", response="hi")
        assert out is None
