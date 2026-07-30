"""Tool router — deterministic tools before LLM."""

from __future__ import annotations

from enum import Enum
from typing import Any

from app.cognitive.events import IntentType


class ToolName(str, Enum):
    CURRICULUM_KB = "curriculum_knowledge_base"
    WEB_SEARCH = "web_search"
    LEXICON = "lexicon_api"
    SPEECH_EVAL = "speech_evaluation"
    COMPETENCY_ENGINE = "competency_engine"
    LESSON_PLANNER = "lesson_planner"
    RAG_SCENARIO = "rag_scenario"
    LEARNING_MEMORY = "learning_memory"
    STUDENT_PROFILE = "student_profile"
    CONVERSATION_MEMORY = "conversation_memory"
    TRANSLATION = "translation_api"
    UTILITY = "utility_tool"
    SCORING_ENGINE = "scoring_engine"
    GRAMMAR_ANALYZER = "grammar_analyzer"
    VOCAB_ANALYZER = "vocabulary_analyzer"
    FLUENCY_ANALYZER = "fluency_analyzer"
    PRONUNCIATION_ANALYZER = "pronunciation_analyzer"
    ASSESSMENT = "assessment_engine"
    STUDENT_MODEL = "student_model"


INTENT_TOOL_MAP: dict[IntentType, list[ToolName]] = {
    IntentType.GREETING: [ToolName.CONVERSATION_MEMORY, ToolName.STUDENT_PROFILE],
    IntentType.CONVERSATION: [ToolName.CONVERSATION_MEMORY, ToolName.LEARNING_MEMORY, ToolName.STUDENT_PROFILE],
    IntentType.TEACHING: [
        ToolName.CURRICULUM_KB, ToolName.LEARNING_MEMORY, ToolName.STUDENT_PROFILE,
        ToolName.GRAMMAR_ANALYZER, ToolName.ASSESSMENT,
    ],
    IntentType.GRAMMAR_EXPLAIN: [
        ToolName.CURRICULUM_KB, ToolName.LEARNING_MEMORY, ToolName.GRAMMAR_ANALYZER,
    ],
    IntentType.SCENARIO_PRACTICE: [
        ToolName.RAG_SCENARIO, ToolName.STUDENT_PROFILE, ToolName.ASSESSMENT,
    ],
    IntentType.TRANSLATION: [ToolName.TRANSLATION, ToolName.LEXICON],
    IntentType.WEB_KNOWLEDGE: [ToolName.WEB_SEARCH],
    IntentType.CONTINUE_LESSON: [
        ToolName.CONVERSATION_MEMORY, ToolName.LEARNING_MEMORY, ToolName.LESSON_PLANNER,
    ],
    IntentType.HOMEWORK: [ToolName.LESSON_PLANNER, ToolName.LEARNING_MEMORY],
    IntentType.QUIZ: [ToolName.CURRICULUM_KB, ToolName.ASSESSMENT],
    IntentType.UTILITY: [ToolName.UTILITY],
    IntentType.PRONUNCIATION_PRACTICE: [
        ToolName.SPEECH_EVAL, ToolName.PRONUNCIATION_ANALYZER, ToolName.LEARNING_MEMORY,
    ],
}


def select_tools(
    intent: IntentType,
    *,
    has_voice: bool = False,
    web_allowed: bool = True,
) -> list[ToolName]:
    tools = list(INTENT_TOOL_MAP.get(intent, [ToolName.CONVERSATION_MEMORY, ToolName.STUDENT_PROFILE]))

    if has_voice:
        for t in (
            ToolName.SPEECH_EVAL,
            ToolName.FLUENCY_ANALYZER,
            ToolName.PRONUNCIATION_ANALYZER,
            ToolName.GRAMMAR_ANALYZER,
            ToolName.VOCAB_ANALYZER,
            ToolName.ASSESSMENT,
            ToolName.STUDENT_MODEL,
        ):
            if t not in tools:
                tools.append(t)

    if intent == IntentType.WEB_KNOWLEDGE and not web_allowed:
        tools = [t for t in tools if t != ToolName.WEB_SEARCH]
        if ToolName.CURRICULUM_KB not in tools:
            tools.insert(0, ToolName.CURRICULUM_KB)

    # Dedupe preserving order
    seen: set[ToolName] = set()
    ordered: list[ToolName] = []
    for t in tools:
        if t not in seen:
            seen.add(t)
            ordered.append(t)
    return ordered


def tools_to_skip(intent: IntentType, selected: list[ToolName]) -> list[str]:
    all_possible = set()
    for tool_list in INTENT_TOOL_MAP.values():
        all_possible.update(tool_list)
    if IntentType.TEACHING in INTENT_TOOL_MAP:
        all_possible.update(INTENT_TOOL_MAP[IntentType.TEACHING])
    skipped = [t.value for t in all_possible if t not in selected]
    return skipped[:8]
