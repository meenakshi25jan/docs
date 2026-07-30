"""LLM router — orchestrator picks model; Teacher Brain stays unaware."""

from __future__ import annotations

from app.cognitive.agent_planner import AgentName
from app.cognitive.events import IntentType


def select_model_tier(
    intent: IntentType,
    agents: list[AgentName],
    message: str,
    policy_tier: str = "full",
) -> str:
    if policy_tier == "mini":
        return "mini"

    if intent in (IntentType.GREETING, IntentType.UTILITY, IntentType.CONVERSATION):
        if len(message.split()) < 10:
            return "mini"

    if intent in (IntentType.GRAMMAR_EXPLAIN, IntentType.HOMEWORK, IntentType.CONTINUE_LESSON):
        return "full"

    if AgentName.PLANNER in agents:
        return "full"

    if intent in (IntentType.TEACHING, IntentType.SCENARIO_PRACTICE, IntentType.WEB_KNOWLEDGE):
        return "full"

    return "mini"
