"""Tests for Wave 1 orchestration foundation."""

from unittest.mock import AsyncMock, patch

import pytest

from app.agents.base import AgentOutput
from app.orchestration.cost_router import select_model_hint
from app.orchestration.moderation import moderate_text
from app.orchestration.orchestrator import classify_intent
from app.orchestration.rag_agent import retrieve
from app.orchestration.runner import run_conversation_turn


class TestOrchestrator:
    def test_greeting_routes_to_conversation(self):
        intent, agent = classify_intent("Hello!")
        assert intent == "greeting"
        assert agent == "ConversationAgent"

    def test_teaching_question_routes_to_teacher(self):
        intent, agent = classify_intent("Can you explain present perfect?")
        assert intent == "teaching"
        assert agent == "TeacherAgent"

    def test_scenario_routes_to_teacher(self):
        intent, agent = classify_intent("I would like the soup.", scenario="restaurant")
        assert intent == "teaching"
        assert agent == "TeacherAgent"


class TestCostRouter:
    def test_greeting_uses_mini(self):
        assert select_model_hint("greeting", "Hello") == "mini"

    def test_teaching_uses_full(self):
        assert select_model_hint("teaching", "Explain conditionals with examples") == "full"


class TestModeration:
    def test_safe_input(self):
        result = moderate_text("Let's practice English grammar.")
        assert result["safe"] is True

    def test_blocks_unsafe_input(self):
        result = moderate_text("how to make a bomb")
        assert result["safe"] is False
        assert result["action"] == "block"


class TestRAG:
    @pytest.mark.asyncio
    async def test_retrieves_grammar_topic(self):
        chunks = await retrieve("explain present perfect tense")
        assert chunks
        assert any("present perfect" in c["topic"] for c in chunks)

    @pytest.mark.asyncio
    async def test_empty_query_returns_empty(self):
        assert await retrieve("") == []


class TestConversationRunner:
    @pytest.mark.asyncio
    async def test_run_conversation_turn_with_mock_agents(self):
        async def fake_teacher_brain(context, **kwargs):
            return {
                "response": "Present perfect uses have/has + past participle.",
                "grammar_corrections": [],
            }

        with patch(
            "app.cognitive.orchestrator.execute_teacher_brain",
            side_effect=fake_teacher_brain,
        ):
            with patch(
                "app.services.memory_intelligence_service.MemoryIntelligenceService.write_after_teacher_turn",
                new_callable=AsyncMock,
            ):
                output = await run_conversation_turn(
                    session_id="test-session-1",
                    learner_id="learner-1",
                    tenant_id=None,
                    scenario="general_conversation",
                    cefr_level="B1",
                    message="Explain present perfect",
                    message_history=[],
                )
        assert "present perfect" in output.data.get("response", "").lower()
        assert output.metadata.get("orchestration") == "cognitive"
        assert "teacher_brain" in str(output.metadata.get("cognitive_trace", {}))
