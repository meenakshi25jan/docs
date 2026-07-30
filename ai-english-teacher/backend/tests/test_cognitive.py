"""Tests for Layer 1 Cognitive Orchestration."""

import pytest

from app.cognitive.events import EventType, IntentType
from app.cognitive.intent_classifier import classify_intent
from app.cognitive.agent_planner import plan_agents, AgentName
from app.cognitive.tool_router import select_tools, ToolName
from app.cognitive.workflow_manager import get_workflow, WorkflowStep
from app.cognitive.web_gateway import needs_external_knowledge
from app.cognitive.policy_engine import evaluate_policy


class TestIntentClassifier:
    def test_greeting(self):
        assert classify_intent("Hello") == IntentType.GREETING

    def test_grammar_explain(self):
        assert classify_intent("Explain present perfect tense") == IntentType.GRAMMAR_EXPLAIN

    def test_web_knowledge(self):
        assert classify_intent("What is the latest AI news today?") == IntentType.WEB_KNOWLEDGE

    def test_translation(self):
        assert classify_intent("Translate this to English") == IntentType.TRANSLATION

    def test_continue_lesson(self):
        assert classify_intent("Continue yesterday's lesson") == IntentType.CONTINUE_LESSON

    def test_scenario_practice(self):
        assert classify_intent("Let's practice job interview", "job_interview") == IntentType.SCENARIO_PRACTICE


class TestToolRouter:
    def test_teaching_includes_coaches_with_voice(self):
        tools = select_tools(IntentType.TEACHING, has_voice=True)
        assert ToolName.GRAMMAR_ANALYZER in tools
        assert ToolName.ASSESSMENT in tools

    def test_web_intent_includes_search(self):
        tools = select_tools(IntentType.WEB_KNOWLEDGE)
        assert ToolName.WEB_SEARCH in tools

    def test_grammar_explain_skips_web(self):
        tools = select_tools(IntentType.GRAMMAR_EXPLAIN)
        assert ToolName.WEB_SEARCH not in tools


class TestAgentPlanner:
    def test_yesterday_i_go_invokes_grammar_not_web(self):
        intent = classify_intent("Yesterday I go market.")
        plan = plan_agents(intent, select_tools(intent, has_voice=True))
        assert AgentName.GRAMMAR in plan.agents
        assert AgentName.WEB_SUMMARIZER not in plan.agents

    def test_web_intent_includes_summarizer(self):
        plan = plan_agents(IntentType.WEB_KNOWLEDGE, [ToolName.WEB_SEARCH])
        assert AgentName.WEB_SUMMARIZER in plan.agents


class TestWorkflowManager:
    def test_grammar_correction_workflow(self):
        wf = get_workflow(IntentType.TEACHING, has_voice=True)
        assert WorkflowStep.TEACHER_BRAIN in wf.steps
        assert WorkflowStep.VOICE_COACHES in wf.steps

    def test_web_workflow(self):
        wf = get_workflow(IntentType.WEB_KNOWLEDGE)
        assert WorkflowStep.WEB_GATEWAY in wf.steps


class TestWebGateway:
    def test_grammar_no_web(self):
        assert needs_external_knowledge(IntentType.GRAMMAR_EXPLAIN, "explain past tense") is False

    def test_news_needs_web(self):
        assert needs_external_knowledge(IntentType.WEB_KNOWLEDGE, "latest news") is True


class TestPolicyEngine:
    def test_low_token_budget_mini_model(self):
        decision = evaluate_policy(tools=[ToolName.WEB_SEARCH], token_budget_remaining=100)
        assert decision.model_tier == "mini"
