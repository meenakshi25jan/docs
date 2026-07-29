"""Curriculum snippets for keyword RAG fallback."""

from __future__ import annotations

import re

CURRICULUM_SNIPPETS: list[dict[str, str]] = [
    {
        "topic": "present perfect",
        "source": "Grammar Unit 4",
        "text": "Present perfect connects past actions to now: have/has + past participle. "
        "Use for life experience, unfinished time, and recent past with present relevance.",
    },
    {
        "topic": "articles",
        "source": "Grammar Unit 2",
        "text": "Use 'a/an' for non-specific singular nouns; 'the' for specific nouns; "
        "omit articles with general plural or uncountable nouns in general statements.",
    },
    {
        "topic": "conditionals",
        "source": "Grammar Unit 7",
        "text": "Zero conditional: if + present, present (facts). First: if + present, will (real future). "
        "Second: if + past, would (hypothetical present). Third: if + past perfect, would have (past hypothetical).",
    },
    {
        "topic": "restaurant",
        "source": "Conversation Scenario",
        "text": "Useful phrases: 'Could I see the menu?', 'I'd like to order...', "
        "'Could we have the bill, please?', 'Is service included?'",
    },
    {
        "topic": "job interview",
        "source": "Conversation Scenario",
        "text": "Structure answers with STAR: Situation, Task, Action, Result. "
        "Use professional vocabulary and past tense for experience questions.",
    },
    {
        "topic": "ielts writing",
        "source": "IELTS Prep",
        "text": "Task 2 essay: introduction with paraphrased question + thesis, "
        "2 body paragraphs with topic sentences and examples, conclusion summarizing without new ideas.",
    },
]


def tokenize(text: str) -> set[str]:
    return set(re.findall(r"[a-z]{3,}", text.lower()))
