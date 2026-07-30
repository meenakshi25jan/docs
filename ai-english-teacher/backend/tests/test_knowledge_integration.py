"""Knowledge Intelligence integration tests."""

from unittest.mock import AsyncMock, patch

import pytest

from app.cognitive.tool_executor import execute_teacher_brain
from app.cognitive.observability import CognitiveTrace


class TestKnowledgeIntegration:
    @pytest.mark.asyncio
    async def test_teacher_brain_grounding_injection(self):
        context = {
            "scenario": "everyday",
            "cefr_level": "B1",
            "message": "I am go to market yesterday.",
            "message_history": [],
            "recent_errors": [],
            "teaching_instruction": "Address the grammar error.",
            "grounding_context": "Use past simple for completed past actions.",
            "voice_summary": "Fluency 70",
            "memory_summary": "",
        }
        trace = CognitiveTrace(trace_id="test-trace")

        with patch(
            "app.orchestration.teacher_brain.teacher_brain_service.TeacherBrainService.process_turn",
            new_callable=AsyncMock,
            return_value=type(
                "R",
                (),
                {
                    "agent_output": {"response": "You went to the market yesterday.", "teacher_brain": {}},
                },
            )(),
        ):
            result = await execute_teacher_brain(
                context,
                learner_id="learner-1",
                tenant_id=None,
                intent="teaching",
                trace=trace,
            )
        assert result.get("response")

    @pytest.mark.asyncio
    async def test_voice_turn_grounding_metadata(self, client, learner_id):
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
                "details": {"grammar": {"errors": [{"text": "am go", "correction": "went"}]}},
            },
        ), patch(
            "app.orchestration.runner.run_conversation_turn",
            new_callable=AsyncMock,
            return_value=type(
                "O",
                (),
                {
                    "data": {"response": "Try: I went to the market yesterday."},
                    "metadata": {
                        "knowledge_grounding": {
                            "lesson_id": "grammar-6-past-simple",
                            "skill_focus": "grammar",
                            "chunk_count": 1,
                            "sources": ["grammar_curriculum"],
                            "fallback_used": False,
                        },
                        "teacher_brain": {"intent": "grammar_correction"},
                    },
                },
            )(),
        ):
            from app.api.v1.conversations import router
            # Direct voice_turn call
            from app.orchestration.voice.voice_turn import run_voice_turn

            result = await run_voice_turn(
                session_id="sess-1",
                learner_id=str(learner_id),
                tenant_id=None,
                scenario="everyday",
                cefr_level="B1",
                message_history=[],
                transcript="I am go to market yesterday.",
            )
        assert result.get("response")
        assert result.get("knowledge_grounding") is not None

    @pytest.mark.asyncio
    async def test_existing_rag_tests_still_pass(self):
        from app.orchestration.rag_agent import retrieve

        chunks = await retrieve("explain present perfect tense")
        assert chunks
