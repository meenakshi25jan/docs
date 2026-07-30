"""Tests for Teacher Brain v1."""

from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest
from httpx import AsyncClient

from app.orchestration.teacher_brain.error_detector import detect_errors
from app.orchestration.teacher_brain.intent_analyzer import analyze_intent
from app.orchestration.teacher_brain.response_planner import plan_response
from app.orchestration.teacher_brain.schemas import DetectedError, IntentAnalysis, TeacherBrainInput
from app.orchestration.teacher_brain.teaching_strategy_selector import select_teaching_strategy
from app.orchestration.teacher_brain.teacher_brain_service import TeacherBrainService
from app.schemas.student_intelligence import (
    StudentProfileResponse,
    StudentSkillsResponse,
    StudentSummaryResponse,
)


class TestIntentAnalyzer:
    def test_greeting(self):
        result = analyze_intent("Hello!")
        assert result.intent == "greeting"
        assert result.confidence >= 0.8

    def test_grammar_question(self):
        result = analyze_intent("Can you explain past tense?")
        assert result.intent == "grammar_question"

    def test_roleplay_practice(self):
        result = analyze_intent("I would like the soup.", scenario="restaurant")
        assert result.intent == "roleplay_practice"

    def test_exam_practice_persona(self):
        result = analyze_intent("Let's begin part two.", persona_id="ielts_examiner")
        assert result.intent == "exam_practice"

    def test_unknown_empty(self):
        result = analyze_intent("")
        assert result.intent == "unknown"


class TestErrorDetector:
    def test_voice_analysis_grammar_errors(self):
        voice = {
            "details": {
                "grammar": {
                    "errors": [
                        {"text": "I am go", "correction": "I went", "severity": "high", "category": "tense"},
                    ],
                },
            },
        }
        errors = detect_errors("I am go to market yesterday.", voice_analysis=voice)
        assert len(errors) >= 1
        assert errors[0].source == "voice_analysis"

    def test_empty_input(self):
        assert detect_errors("") == []

    def test_heuristic_past_tense(self):
        errors = detect_errors("I am go to market yesterday.")
        assert any(e.type == "grammar" for e in errors)


class TestStrategySelector:
    def test_low_confidence_encouragement(self):
        si = StudentSummaryResponse(
            profile=StudentProfileResponse(user_id=uuid4(), confidence_score=0.3),
            skills=StudentSkillsResponse(),
            has_data=True,
        )
        intent = IntentAnalysis(intent="practice_continuation", confidence=0.6)
        strategy = select_teaching_strategy(
            intent, [],
            student_intelligence_summary=si,
        )
        assert strategy == "encouragement_first"

    def test_grammar_question_explanation(self):
        intent = IntentAnalysis(intent="grammar_question", confidence=0.8)
        strategy = select_teaching_strategy(intent, [])
        assert strategy == "explanation_first"

    def test_roleplay_continuation(self):
        intent = IntentAnalysis(intent="roleplay_practice", confidence=0.7)
        strategy = select_teaching_strategy(intent, [], scenario="restaurant")
        assert strategy == "roleplay_continuation"

    def test_exam_coaching_persona(self):
        intent = IntentAnalysis(intent="practice_continuation", confidence=0.6)
        strategy = select_teaching_strategy(intent, [], persona_id="ielts_examiner")
        assert strategy == "exam_coaching"

    def test_repeated_grammar_scaffold(self):
        intent = IntentAnalysis(intent="practice_continuation", confidence=0.6)
        errors = [
            DetectedError(type="grammar", original_text="a", severity="medium", source="voice"),
            DetectedError(type="grammar", original_text="b", severity="medium", source="voice"),
        ]
        strategy = select_teaching_strategy(intent, errors, teaching_mode="delayed")
        assert strategy == "scaffold"


class TestResponsePlanner:
    def test_spoken_friendly_plan(self):
        intent = IntentAnalysis(intent="practice_continuation", confidence=0.6)
        plan = plan_response(intent, "practice_prompt", [], is_voice_turn=True)
        assert plan.max_sentences <= 4
        assert plan.include_encouragement

    def test_includes_next_prompt(self):
        intent = IntentAnalysis(intent="grammar_question", confidence=0.8)
        errors = [DetectedError(type="grammar", original_text="I go", suggested_correction="I went", source="v")]
        plan = plan_response(intent, "explanation_first", errors, skill_focus="grammar")
        assert plan.practice_question is not None


class TestTeacherBrainService:
    @pytest.mark.asyncio
    async def test_deterministic_fallback_grammar(self):
        service = TeacherBrainService()
        from app.orchestration.teacher_brain.schemas import ResponsePlan

        plan = ResponsePlan(skill_focus="grammar", practice_question="Try again.")
        text = service._deterministic_fallback(
            "I am go to market yesterday.",
            [],
            plan,
        )
        assert "went" in text.lower() or "try" in text.lower()

    @pytest.mark.asyncio
    async def test_process_turn_with_mock_agent(self):
        service = TeacherBrainService()
        tb_input = TeacherBrainInput(
            message="Hello!",
            scenario="general_conversation",
            persona_id="conversation_partner",
            orchestration_intent="greeting",
        )
        agent_context = {
            "scenario": "general_conversation",
            "cefr_level": "B1",
            "message": "Hello!",
            "message_history": [],
            "teaching_mode": "none",
            "teaching_instruction": "Respond naturally.",
            "voice_summary": "not available",
        }
        with patch(
            "app.orchestration.conversation_agent.ConversationAgent",
        ) as mock_cls:
            mock_cls.return_value.execute = AsyncMock(
                return_value=MagicMock(data={"response": "Hello! Welcome to our practice session."}),
            )
            result = await service.process_turn(
                tb_input,
                agent_context=agent_context,
                learner_id=str(uuid4()),
                tenant_id=None,
                use_conversation_agent=True,
            )
            assert result.teacher_response
            assert result.metadata["source"] == "teacher_brain_v1"
            assert "teacher_brain" in result.agent_output

    @pytest.mark.asyncio
    async def test_si_unavailable_still_works(self):
        service = TeacherBrainService()
        tb_input = TeacherBrainInput(message="Hi there", scenario="everyday")
        agent_context = {
            "scenario": "everyday",
            "cefr_level": "B1",
            "message": "Hi there",
            "message_history": [],
            "teaching_mode": "none",
            "teaching_instruction": "",
            "voice_summary": "not available",
        }
        with patch.object(service, "_try_fetch_si_summary", return_value=None):
            with patch(
                "app.orchestration.teacher_brain.teacher_brain_service.AGENT_REGISTRY",
            ) as mock_registry:
                mock_teacher = MagicMock()
                mock_teacher.execute = AsyncMock(
                    return_value=MagicMock(data={"response": "Hi! How are you today?"}),
                )
                mock_registry.__getitem__ = MagicMock(return_value=mock_teacher)
                result = await service.process_turn(
                    tb_input,
                    agent_context=agent_context,
                    learner_id=str(uuid4()),
                    tenant_id=None,
                )
                assert result.metadata["si_available"] is False
                assert result.teacher_response


class TestTeacherBrainAPI:
    @pytest.mark.asyncio
    async def test_voice_turn_core_fields(self, client: AsyncClient, learner_id):
        mock_result = {
            "transcript": "Hello",
            "response": "Welcome!",
            "teaching_mode": "none",
            "corrections": [],
            "voice_scores": {"overall": 80},
            "estimates": {"cefr": "B1"},
            "teacher_brain": {
                "intent": "greeting",
                "teaching_strategy": "practice_prompt",
                "skill_focus": "speaking",
                "correction_mode": "none",
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
            assert data["response"] == "Welcome!"
            assert data["teaching_mode"] == "none"
            assert data["corrections"] == []
            assert data["teacher_brain"]["intent"] == "greeting"

    @pytest.mark.asyncio
    async def test_conversation_voice_turn_backward_compat(self, client: AsyncClient, learner_id):
        from app.models import Conversation

        conv_id = uuid4()
        conv = MagicMock(spec=Conversation)
        conv.id = conv_id
        conv.scenario = "everyday"
        conv.context = {}
        conv.messages = []

        mock_result = {
            "transcript": "I am go to market yesterday.",
            "response": "Good try. Use went for past tense.",
            "teaching_mode": "immediate",
            "corrections": [{"wrong": "am go", "correct": "went"}],
            "voice_scores": {"overall": 70},
            "estimates": {},
            "teacher_brain": {
                "intent": "practice_continuation",
                "teaching_strategy": "immediate_correction",
                "skill_focus": "grammar",
            },
            "agent_output": {},
            "metadata": {},
        }
        client.mock_db.scalar = AsyncMock(side_effect=[conv, client.mock_learner])
        with patch(
            "app.api.v1.conversations.run_voice_turn",
            return_value=mock_result,
        ):
            res = await client.post(
                f"/api/v1/conversations/{conv_id}/voice-turn",
                json={"transcript": "I am go to market yesterday."},
            )
            assert res.status_code == 200
            data = res.json()
            assert "response" in data
            assert "voice_scores" in data
            assert data.get("teacher_brain") is not None
