"""Curriculum registry — single source of truth for topics, skills, lessons, and paths."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from app.orchestration.personas import PERSONAS, SCENARIOS, list_personas, list_scenarios
from app.services.grammar_curriculum import GRADE_LEVELS, GRAMMAR_LESSONS

CEFR_TO_GRADE: dict[str, int] = {
    "A1": 5,
    "A2": 7,
    "B1": 9,
    "B2": 11,
    "C1": 12,
    "C2": 12,
}

TOPIC_IDS = [
    "grammar",
    "vocabulary",
    "speaking",
    "pronunciation",
    "fluency",
    "listening",
    "writing",
    "exam_preparation",
]


@dataclass
class CurriculumTopic:
    id: str
    title: str
    description: str


@dataclass
class CurriculumSkill:
    id: str
    topic_id: str
    title: str
    description: str


@dataclass
class CurriculumLesson:
    lesson_id: str
    title: str
    topic_id: str
    skill_id: str
    skill_focus: str
    route: str
    cefr_level: str = "B1"
    description: str = ""
    prerequisites: list[str] = field(default_factory=list)
    exam_tag: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class SkillPrerequisite:
    skill_id: str
    requires_skill_id: str
    min_score: float = 50.0


@dataclass
class LearningPathTemplate:
    path_id: str
    title: str
    description: str
    lesson_ids: list[str] = field(default_factory=list)


def _grammar_lesson_id(grade: int, lesson_slug: str) -> str:
    return f"grammar-{grade}-{lesson_slug}"


def _build_lessons() -> dict[str, CurriculumLesson]:
    lessons: dict[str, CurriculumLesson] = {}

    for grade, items in GRAMMAR_LESSONS.items():
        cefr = GRADE_LEVELS.get(grade, {}).get("cefr", "B1")
        for item in items:
            lid = _grammar_lesson_id(grade, item["id"])
            lessons[lid] = CurriculumLesson(
                lesson_id=lid,
                title=item["title"],
                topic_id="grammar",
                skill_id="grammar",
                skill_focus="grammar",
                route=f"/grammar-class?grade={grade}&lesson_id={item['id']}",
                cefr_level=cefr,
                description=item.get("rule", ""),
                metadata={"grade": grade, "grammar_lesson_id": item["id"]},
            )

    for scenario_id, scenario in SCENARIOS.items():
        lid = f"speaking-{scenario_id}"
        lessons[lid] = CurriculumLesson(
            lesson_id=lid,
            title=f"Speaking: {scenario['label']}",
            topic_id="speaking",
            skill_id="speaking",
            skill_focus="speaking",
            route=f"/conversation?scenario={scenario_id}",
            cefr_level="B1",
            description=f"Practice conversation in a {scenario['label']} scenario.",
            metadata={"scenario": scenario_id},
        )

    for persona_id in ("ielts_examiner", "pte_coach", "toefl_trainer"):
        persona = PERSONAS.get(persona_id, {})
        lid = f"exam-{persona_id.replace('_', '-')}"
        exam_tag = "ielts" if "ielts" in persona_id else "pte" if "pte" in persona_id else "toefl"
        lessons[lid] = CurriculumLesson(
            lesson_id=lid,
            title=persona.get("label", persona_id),
            topic_id="exam_preparation",
            skill_id="exam_preparation",
            skill_focus="speaking",
            route=f"/conversation?persona_id={persona_id}&scenario=general_conversation",
            cefr_level="B1",
            description=persona.get("description", ""),
            exam_tag=exam_tag,
            metadata={"persona_id": persona_id},
        )

    lessons["placement-assessment"] = CurriculumLesson(
        lesson_id="placement-assessment",
        title="Placement Assessment",
        topic_id="exam_preparation",
        skill_id="listening",
        skill_focus="general",
        route="/assessment",
        cefr_level="A1",
        description="Complete a placement assessment to personalize your learning path.",
    )

    lessons["confidence-friendly-beginner"] = CurriculumLesson(
        lesson_id="confidence-friendly-beginner",
        title="Confidence Builder Conversation",
        topic_id="speaking",
        skill_id="fluency",
        skill_focus="fluency",
        route="/conversation?persona_id=friendly_beginner&scenario=everyday",
        cefr_level="A1",
        description="Low-pressure speaking with a warm beginner-friendly teacher.",
        metadata={"persona_id": "friendly_beginner", "scenario": "everyday"},
    )

    lessons["pronunciation-practice"] = CurriculumLesson(
        lesson_id="pronunciation-practice",
        title="Pronunciation Practice",
        topic_id="pronunciation",
        skill_id="pronunciation",
        skill_focus="pronunciation",
        route="/conversation?scenario=everyday&persona_id=conversation_partner",
        cefr_level="B1",
        description="Focus on clear pronunciation and natural rhythm in short spoken turns.",
    )

    lessons["fluency-conversation"] = CurriculumLesson(
        lesson_id="fluency-conversation",
        title="Fluency Conversation Practice",
        topic_id="fluency",
        skill_id="fluency",
        skill_focus="fluency",
        route="/conversation?scenario=general_conversation&persona_id=conversation_partner",
        cefr_level="B1",
        description="Build speaking fluency through extended conversation practice.",
    )

    lessons["vocabulary-daily"] = CurriculumLesson(
        lesson_id="vocabulary-daily",
        title="Daily Vocabulary Builder",
        topic_id="vocabulary",
        skill_id="vocabulary",
        skill_focus="vocabulary",
        route="/conversation?scenario=everyday",
        cefr_level="B1",
        description="Learn and practice useful everyday vocabulary in context.",
    )

    return lessons


_LESSONS: dict[str, CurriculumLesson] = _build_lessons()

_TOPICS: list[CurriculumTopic] = [
    CurriculumTopic("grammar", "Grammar", "Sentence structure, tenses, and accuracy."),
    CurriculumTopic("vocabulary", "Vocabulary", "Word choice and lexical range."),
    CurriculumTopic("speaking", "Speaking", "Interactive spoken communication."),
    CurriculumTopic("pronunciation", "Pronunciation", "Sounds, clarity, and intelligibility."),
    CurriculumTopic("fluency", "Fluency", "Smooth, confident speech flow."),
    CurriculumTopic("listening", "Listening", "Comprehension and response."),
    CurriculumTopic("writing", "Writing", "Structured written English."),
    CurriculumTopic("exam_preparation", "Exam Preparation", "IELTS, PTE, and TOEFL speaking practice."),
]

_SKILLS: list[CurriculumSkill] = [
    CurriculumSkill("grammar", "grammar", "Grammar", "Accuracy and sentence structure"),
    CurriculumSkill("vocabulary", "vocabulary", "Vocabulary", "Word knowledge and usage"),
    CurriculumSkill("speaking", "speaking", "Speaking", "Spoken communication"),
    CurriculumSkill("pronunciation", "pronunciation", "Pronunciation", "Clear speech sounds"),
    CurriculumSkill("fluency", "fluency", "Fluency", "Smooth speech flow"),
    CurriculumSkill("listening", "listening", "Listening", "Understanding spoken English"),
    CurriculumSkill("writing", "writing", "Writing", "Written expression"),
    CurriculumSkill("exam_preparation", "exam_preparation", "Exam Prep", "Test-oriented practice"),
]

_PREREQUISITES: list[SkillPrerequisite] = [
    SkillPrerequisite("fluency", "speaking", 45.0),
    SkillPrerequisite("pronunciation", "speaking", 40.0),
]

_PATHS: dict[str, LearningPathTemplate] = {
    "daily": LearningPathTemplate(
        path_id="daily",
        title="Daily Learning Path",
        description="One revision, one weak-skill lesson, and one speaking practice.",
        lesson_ids=["revision-placeholder", "grammar-9-modal-verbs", "speaking-everyday"],
    ),
    "weekly": LearningPathTemplate(
        path_id="weekly",
        title="Weekly Learning Path",
        description="Three lessons, two scenarios, revision, and assessment checkpoint.",
        lesson_ids=[
            "grammar-9-conditionals-1",
            "grammar-9-relative-clauses",
            "speaking-restaurant",
            "speaking-travel",
            "placement-assessment",
        ],
    ),
    "exam": LearningPathTemplate(
        path_id="exam",
        title="Exam Preparation Path",
        description="Exam-tagged lessons with speaking-first progression.",
        lesson_ids=["exam-ielts-examiner", "exam-pte-coach", "speaking-job_interview"],
    ),
    "repair": LearningPathTemplate(
        path_id="repair",
        title="Skill Repair Path",
        description="Focus on the weakest skill until it improves.",
        lesson_ids=["grammar-8-present-perfect", "pronunciation-practice"],
    ),
    "confidence": LearningPathTemplate(
        path_id="confidence",
        title="Confidence Building Path",
        description="Friendly beginner persona and low-pressure scenarios.",
        lesson_ids=["confidence-friendly-beginner", "speaking-everyday", "speaking-general_conversation"],
    ),
}


def get_topics() -> list[CurriculumTopic]:
    return list(_TOPICS)


def get_skills(topic_id: str | None = None) -> list[CurriculumSkill]:
    if topic_id:
        return [s for s in _SKILLS if s.topic_id == topic_id]
    return list(_SKILLS)


def get_lessons(
    *,
    topic_id: str | None = None,
    skill_focus: str | None = None,
    cefr_level: str | None = None,
) -> list[CurriculumLesson]:
    result = list(_LESSONS.values())
    if topic_id:
        result = [l for l in result if l.topic_id == topic_id]
    if skill_focus:
        result = [l for l in result if l.skill_focus == skill_focus]
    if cefr_level:
        result = [l for l in result if l.cefr_level == cefr_level]
    return result


def get_lesson(lesson_id: str) -> CurriculumLesson | None:
    return _LESSONS.get(lesson_id)


def get_paths() -> list[LearningPathTemplate]:
    return list(_PATHS.values())


def get_path(path_id: str) -> LearningPathTemplate | None:
    return _PATHS.get(path_id)


def get_next_cefr_lesson(cefr_level: str, completed_ids: set[str]) -> CurriculumLesson | None:
    grade = CEFR_TO_GRADE.get(cefr_level.upper(), 9)
    for g in range(grade, 13):
        for item in GRAMMAR_LESSONS.get(g, []):
            lid = _grammar_lesson_id(g, item["id"])
            if lid not in completed_ids:
                return _LESSONS.get(lid)
    for lesson in _LESSONS.values():
        if lesson.lesson_id.startswith("speaking-") and lesson.lesson_id not in completed_ids:
            return lesson
    return None


def get_grammar_lesson_for_mistake(category: str, cefr_level: str = "B1") -> CurriculumLesson | None:
    grade = CEFR_TO_GRADE.get(cefr_level.upper(), 9)
    if category in ("grammar", "tense", "sentence_structure"):
        lessons = GRAMMAR_LESSONS.get(grade, GRAMMAR_LESSONS.get(9, []))
        if lessons:
            lid = _grammar_lesson_id(grade, lessons[0]["id"])
            found = _LESSONS.get(lid)
            if found:
                return found
        lid = _grammar_lesson_id(9, "modal-verbs")
        return _LESSONS.get(lid)
    return _LESSONS.get("grammar-9-modal-verbs")


def list_registry_metadata() -> dict[str, Any]:
    return {
        "topics": len(_TOPICS),
        "skills": len(_SKILLS),
        "lessons": len(_LESSONS),
        "paths": len(_PATHS),
        "personas": list_personas(),
        "scenarios": list_scenarios(),
    }
