"""Agent planner — invoke only required specialists."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from app.cognitive.events import IntentType
from app.cognitive.tool_router import ToolName


class AgentName(str, Enum):
    GRAMMAR = "grammar"
    VOCABULARY = "vocabulary"
    PRONUNCIATION = "pronunciation"
    FLUENCY = "fluency"
    SPEECH_QUALITY = "speech_quality"
    ASSESSMENT = "assessment"
    STUDENT_MODEL = "student_model"
    TEACHER_BRAIN = "teacher_brain"
    CONVERSATION = "conversation"
    PLANNER = "planner"
    REPORT = "report"
    WEB_SUMMARIZER = "web_summarizer"
    TRANSLATION = "translation"


TOOL_AGENT_MAP: dict[ToolName, list[AgentName]] = {
    ToolName.GRAMMAR_ANALYZER: [AgentName.GRAMMAR],
    ToolName.VOCAB_ANALYZER: [AgentName.VOCABULARY],
    ToolName.PRONUNCIATION_ANALYZER: [AgentName.PRONUNCIATION],
    ToolName.FLUENCY_ANALYZER: [AgentName.FLUENCY],
    ToolName.SPEECH_EVAL: [AgentName.PRONUNCIATION, AgentName.FLUENCY, AgentName.SPEECH_QUALITY],
    ToolName.ASSESSMENT: [AgentName.ASSESSMENT],
    ToolName.STUDENT_MODEL: [AgentName.STUDENT_MODEL],
    ToolName.LESSON_PLANNER: [AgentName.PLANNER],
    ToolName.WEB_SEARCH: [AgentName.WEB_SUMMARIZER],
    ToolName.TRANSLATION: [AgentName.TRANSLATION],
}


INTENT_REQUIRED_AGENTS: dict[IntentType, list[AgentName]] = {
    IntentType.GREETING: [AgentName.CONVERSATION],
    IntentType.CONVERSATION: [AgentName.TEACHER_BRAIN],
    IntentType.TEACHING: [AgentName.GRAMMAR, AgentName.TEACHER_BRAIN],
    IntentType.GRAMMAR_EXPLAIN: [AgentName.GRAMMAR, AgentName.TEACHER_BRAIN],
    IntentType.SCENARIO_PRACTICE: [AgentName.TEACHER_BRAIN, AgentName.ASSESSMENT],
    IntentType.WEB_KNOWLEDGE: [AgentName.WEB_SUMMARIZER, AgentName.TEACHER_BRAIN],
    IntentType.TRANSLATION: [AgentName.TRANSLATION, AgentName.TEACHER_BRAIN],
    IntentType.CONTINUE_LESSON: [AgentName.TEACHER_BRAIN, AgentName.PLANNER],
    IntentType.HOMEWORK: [AgentName.PLANNER, AgentName.TEACHER_BRAIN],
    IntentType.QUIZ: [AgentName.GRAMMAR, AgentName.VOCABULARY, AgentName.TEACHER_BRAIN],
    IntentType.PRONUNCIATION_PRACTICE: [AgentName.PRONUNCIATION, AgentName.TEACHER_BRAIN],
}


@dataclass
class AgentPlan:
    agents: list[AgentName] = field(default_factory=list)
    skipped: list[str] = field(default_factory=list)
    rationale: str = ""


def plan_agents(intent: IntentType, tools: list[ToolName]) -> AgentPlan:
    agents: list[AgentName] = list(INTENT_REQUIRED_AGENTS.get(intent, [AgentName.TEACHER_BRAIN]))

    for tool in tools:
        for agent in TOOL_AGENT_MAP.get(tool, []):
            if agent not in agents:
                agents.append(agent)

    if AgentName.TEACHER_BRAIN not in agents and intent not in (IntentType.GREETING,):
        agents.append(AgentName.TEACHER_BRAIN)

    all_agents = {a for agents_list in INTENT_REQUIRED_AGENTS.values() for a in agents_list}
    all_agents.update(a for tool_agents in TOOL_AGENT_MAP.values() for a in tool_agents)
    skipped = [a.value for a in all_agents if a not in agents][:10]

    return AgentPlan(
        agents=agents,
        skipped=skipped,
        rationale=f"intent={intent.value}; tools={len(tools)}",
    )
