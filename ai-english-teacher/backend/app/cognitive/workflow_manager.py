"""Workflow definitions — predefined execution paths per intent."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

from app.cognitive.events import IntentType


class WorkflowStep(str, Enum):
    MODERATE_INPUT = "moderate_input"
    STT = "stt"
    INTENT = "intent_classify"
    TOOL_ROUTE = "tool_route"
    MEMORY_ROUTE = "memory_route"
    AGENT_PLAN = "agent_plan"
    EXECUTE_TOOLS = "execute_tools"
    WEB_GATEWAY = "web_gateway"
    VOICE_COACHES = "voice_coaches"
    TEACHING_DECISION = "teaching_decision"
    CONTEXT_BUILD = "context_build"
    TEACHER_BRAIN = "teacher_brain"
    MODERATE_OUTPUT = "moderate_output"
    STATE_PERSIST = "state_persist"
    TTS = "tts"


@dataclass
class WorkflowDefinition:
    name: str
    steps: list[WorkflowStep] = field(default_factory=list)


WORKFLOWS: dict[IntentType, WorkflowDefinition] = {
    IntentType.GREETING: WorkflowDefinition(
        "greeting",
        [WorkflowStep.MODERATE_INPUT, WorkflowStep.INTENT, WorkflowStep.MEMORY_ROUTE,
         WorkflowStep.CONTEXT_BUILD, WorkflowStep.TEACHER_BRAIN, WorkflowStep.MODERATE_OUTPUT],
    ),
    IntentType.CONVERSATION: WorkflowDefinition(
        "conversation",
        [WorkflowStep.MODERATE_INPUT, WorkflowStep.INTENT, WorkflowStep.TOOL_ROUTE,
         WorkflowStep.MEMORY_ROUTE, WorkflowStep.AGENT_PLAN, WorkflowStep.CONTEXT_BUILD,
         WorkflowStep.TEACHER_BRAIN, WorkflowStep.MODERATE_OUTPUT, WorkflowStep.STATE_PERSIST],
    ),
    IntentType.TEACHING: WorkflowDefinition(
        "grammar_correction",
        [WorkflowStep.MODERATE_INPUT, WorkflowStep.STT, WorkflowStep.INTENT, WorkflowStep.TOOL_ROUTE,
         WorkflowStep.MEMORY_ROUTE, WorkflowStep.AGENT_PLAN, WorkflowStep.VOICE_COACHES,
         WorkflowStep.TEACHING_DECISION, WorkflowStep.CONTEXT_BUILD, WorkflowStep.TEACHER_BRAIN,
         WorkflowStep.MODERATE_OUTPUT, WorkflowStep.STATE_PERSIST],
    ),
    IntentType.GRAMMAR_EXPLAIN: WorkflowDefinition(
        "grammar_explain",
        [WorkflowStep.MODERATE_INPUT, WorkflowStep.INTENT, WorkflowStep.TOOL_ROUTE,
         WorkflowStep.MEMORY_ROUTE, WorkflowStep.EXECUTE_TOOLS, WorkflowStep.CONTEXT_BUILD,
         WorkflowStep.TEACHER_BRAIN, WorkflowStep.MODERATE_OUTPUT],
    ),
    IntentType.SCENARIO_PRACTICE: WorkflowDefinition(
        "interview_practice",
        [WorkflowStep.MODERATE_INPUT, WorkflowStep.STT, WorkflowStep.INTENT, WorkflowStep.TOOL_ROUTE,
         WorkflowStep.MEMORY_ROUTE, WorkflowStep.AGENT_PLAN, WorkflowStep.VOICE_COACHES,
         WorkflowStep.TEACHING_DECISION, WorkflowStep.CONTEXT_BUILD, WorkflowStep.TEACHER_BRAIN,
         WorkflowStep.MODERATE_OUTPUT, WorkflowStep.STATE_PERSIST],
    ),
    IntentType.WEB_KNOWLEDGE: WorkflowDefinition(
        "current_affairs",
        [WorkflowStep.MODERATE_INPUT, WorkflowStep.INTENT, WorkflowStep.WEB_GATEWAY,
         WorkflowStep.CONTEXT_BUILD, WorkflowStep.TEACHER_BRAIN, WorkflowStep.MODERATE_OUTPUT],
    ),
    IntentType.TRANSLATION: WorkflowDefinition(
        "translation",
        [WorkflowStep.MODERATE_INPUT, WorkflowStep.INTENT, WorkflowStep.EXECUTE_TOOLS,
         WorkflowStep.CONTEXT_BUILD, WorkflowStep.TEACHER_BRAIN, WorkflowStep.MODERATE_OUTPUT],
    ),
    IntentType.CONTINUE_LESSON: WorkflowDefinition(
        "continue_lesson",
        [WorkflowStep.MODERATE_INPUT, WorkflowStep.INTENT, WorkflowStep.MEMORY_ROUTE,
         WorkflowStep.CONTEXT_BUILD, WorkflowStep.TEACHER_BRAIN, WorkflowStep.MODERATE_OUTPUT],
    ),
    IntentType.HOMEWORK: WorkflowDefinition(
        "homework",
        [WorkflowStep.MODERATE_INPUT, WorkflowStep.INTENT, WorkflowStep.TOOL_ROUTE,
         WorkflowStep.MEMORY_ROUTE, WorkflowStep.AGENT_PLAN, WorkflowStep.CONTEXT_BUILD,
         WorkflowStep.TEACHER_BRAIN, WorkflowStep.MODERATE_OUTPUT],
    ),
    IntentType.QUIZ: WorkflowDefinition(
        "quiz",
        [WorkflowStep.MODERATE_INPUT, WorkflowStep.INTENT, WorkflowStep.TOOL_ROUTE,
         WorkflowStep.EXECUTE_TOOLS, WorkflowStep.CONTEXT_BUILD, WorkflowStep.TEACHER_BRAIN,
         WorkflowStep.MODERATE_OUTPUT],
    ),
    IntentType.PRONUNCIATION_PRACTICE: WorkflowDefinition(
        "pronunciation",
        [WorkflowStep.MODERATE_INPUT, WorkflowStep.STT, WorkflowStep.INTENT, WorkflowStep.VOICE_COACHES,
         WorkflowStep.TEACHING_DECISION, WorkflowStep.CONTEXT_BUILD, WorkflowStep.TEACHER_BRAIN,
         WorkflowStep.MODERATE_OUTPUT, WorkflowStep.STATE_PERSIST],
    ),
    IntentType.UTILITY: WorkflowDefinition(
        "utility",
        [WorkflowStep.MODERATE_INPUT, WorkflowStep.INTENT, WorkflowStep.EXECUTE_TOOLS,
         WorkflowStep.TEACHER_BRAIN, WorkflowStep.MODERATE_OUTPUT],
    ),
}


def get_workflow(intent: IntentType, has_voice: bool = False) -> WorkflowDefinition:
    workflow = WORKFLOWS.get(intent, WORKFLOWS[IntentType.CONVERSATION])
    if has_voice and WorkflowStep.STT not in workflow.steps:
        steps = [WorkflowStep.STT] + list(workflow.steps)
        return WorkflowDefinition(workflow.name + "_voice", steps)
    return workflow
