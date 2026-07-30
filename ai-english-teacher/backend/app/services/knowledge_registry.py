"""In-code knowledge registry — lesson/mistake maps and concepts (v1, no DB)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from app.services.curriculum_registry import get_lesson
from app.services.grammar_curriculum import GRAMMAR_LESSONS, get_lesson as get_grammar_lesson


@dataclass
class KnowledgeConcept:
    key: str
    title: str
    skill_focus: str
    cefr_level: str = "B1"
    exam_tag: str | None = None
    query_terms: list[str] = field(default_factory=list)
    topics: list[str] = field(default_factory=list)


@dataclass
class LessonKnowledgeMapping:
    lesson_id: str
    concept_keys: list[str]
    query_terms: list[str] = field(default_factory=list)
    grammar_grade: int | None = None
    grammar_lesson_id: str | None = None


@dataclass
class MistakeKnowledgeMapping:
    error_category: str
    error_type: str | None
    concept_key: str
    explanation: str
    example: str
    correction: str
    lesson_id: str | None = None


_CONCEPTS: dict[str, KnowledgeConcept] = {
    "articles": KnowledgeConcept(
        key="articles",
        title="Articles (a, an, the)",
        skill_focus="grammar",
        cefr_level="A1",
        query_terms=["articles", "a an the", "article"],
        topics=["articles"],
    ),
    "past_tense": KnowledgeConcept(
        key="past_tense",
        title="Past Simple",
        skill_focus="grammar",
        cefr_level="A2",
        query_terms=["past simple", "past tense", "went", "yesterday"],
        topics=["past simple", "past tense"],
    ),
    "present_perfect": KnowledgeConcept(
        key="present_perfect",
        title="Present Perfect",
        skill_focus="grammar",
        cefr_level="B1",
        query_terms=["present perfect", "have has", "past participle"],
        topics=["present perfect"],
    ),
    "prepositions": KnowledgeConcept(
        key="prepositions",
        title="Prepositions",
        skill_focus="grammar",
        cefr_level="A2",
        query_terms=["prepositions", "in on at", "preposition"],
        topics=["prepositions"],
    ),
    "conditionals": KnowledgeConcept(
        key="conditionals",
        title="Conditionals",
        skill_focus="grammar",
        cefr_level="B1",
        query_terms=["conditional", "if will", "if would"],
        topics=["conditionals", "first conditional", "second conditional"],
    ),
    "sentence_structure": KnowledgeConcept(
        key="sentence_structure",
        title="Sentence Structure",
        skill_focus="grammar",
        cefr_level="B1",
        query_terms=["sentence structure", "subject verb", "word order"],
        topics=["sentence structure", "relative clauses"],
    ),
    "modal_verbs": KnowledgeConcept(
        key="modal_verbs",
        title="Modal Verbs",
        skill_focus="grammar",
        cefr_level="B1",
        query_terms=["modal verbs", "can could must should"],
        topics=["modal verbs"],
    ),
    "restaurant_roleplay": KnowledgeConcept(
        key="restaurant_roleplay",
        title="Restaurant Conversation",
        skill_focus="speaking",
        cefr_level="B1",
        query_terms=["restaurant", "menu", "order", "bill"],
        topics=["restaurant"],
    ),
    "job_interview": KnowledgeConcept(
        key="job_interview",
        title="Job Interview Speaking",
        skill_focus="speaking",
        cefr_level="B2",
        query_terms=["job interview", "STAR", "professional"],
        topics=["job interview"],
    ),
    "ielts_speaking": KnowledgeConcept(
        key="ielts_speaking",
        title="IELTS Speaking",
        skill_focus="exam_preparation",
        cefr_level="B2",
        exam_tag="ielts",
        query_terms=["ielts speaking", "cue card", "part 2", "part 3"],
        topics=["ielts"],
    ),
    "pte_speaking": KnowledgeConcept(
        key="pte_speaking",
        title="PTE Speaking",
        skill_focus="exam_preparation",
        cefr_level="B2",
        exam_tag="pte",
        query_terms=["pte speaking", "describe image", "read aloud"],
        topics=["pte"],
    ),
    "everyday_speaking": KnowledgeConcept(
        key="everyday_speaking",
        title="Everyday Conversation",
        skill_focus="speaking",
        cefr_level="A2",
        query_terms=["everyday", "daily conversation", "small talk"],
        topics=["everyday", "general conversation"],
    ),
    "travel_speaking": KnowledgeConcept(
        key="travel_speaking",
        title="Travel Conversation",
        skill_focus="speaking",
        cefr_level="B1",
        query_terms=["travel", "airport", "hotel", "check in"],
        topics=["travel"],
    ),
}


def _build_lesson_map() -> dict[str, LessonKnowledgeMapping]:
    mappings: dict[str, LessonKnowledgeMapping] = {}

    for grade, items in GRAMMAR_LESSONS.items():
        for item in items:
            lid = f"grammar-{grade}-{item['id']}"
            concept_key = {
                "articles": "articles",
                "past-simple": "past_tense",
                "present-perfect": "present_perfect",
                "prepositions": "prepositions",
                "conditionals-1": "conditionals",
                "conditionals-2": "conditionals",
                "relative-clauses": "sentence_structure",
                "modal-verbs": "modal_verbs",
            }.get(item["id"], "sentence_structure")
            mappings[lid] = LessonKnowledgeMapping(
                lesson_id=lid,
                concept_keys=[concept_key],
                query_terms=[item["title"], item["id"].replace("-", " "), item.get("rule", "")[:80]],
                grammar_grade=grade,
                grammar_lesson_id=item["id"],
            )

    scenario_map = {
        "restaurant": "restaurant_roleplay",
        "job_interview": "job_interview",
        "travel": "travel_speaking",
        "everyday": "everyday_speaking",
        "general_conversation": "everyday_speaking",
    }
    for scenario_id, concept_key in scenario_map.items():
        lid = f"speaking-{scenario_id}"
        concept = _CONCEPTS[concept_key]
        mappings[lid] = LessonKnowledgeMapping(
            lesson_id=lid,
            concept_keys=[concept_key],
            query_terms=list(concept.query_terms),
        )

    mappings["exam-ielts-examiner"] = LessonKnowledgeMapping(
        lesson_id="exam-ielts-examiner",
        concept_keys=["ielts_speaking"],
        query_terms=_CONCEPTS["ielts_speaking"].query_terms,
    )
    mappings["exam-pte-coach"] = LessonKnowledgeMapping(
        lesson_id="exam-pte-coach",
        concept_keys=["pte_speaking"],
        query_terms=_CONCEPTS["pte_speaking"].query_terms,
    )
    mappings["grammar-9-modal-verbs"] = mappings.get(
        "grammar-9-modal-verbs",
        LessonKnowledgeMapping(
            lesson_id="grammar-9-modal-verbs",
            concept_keys=["modal_verbs"],
            query_terms=["modal verbs", "can could must should"],
            grammar_grade=9,
            grammar_lesson_id="modal-verbs",
        ),
    )
    mappings["pronunciation-practice"] = LessonKnowledgeMapping(
        lesson_id="pronunciation-practice",
        concept_keys=["everyday_speaking"],
        query_terms=["pronunciation", "clear speech", "sounds"],
    )
    mappings["confidence-friendly-beginner"] = LessonKnowledgeMapping(
        lesson_id="confidence-friendly-beginner",
        concept_keys=["everyday_speaking"],
        query_terms=["beginner", "confidence", "easy conversation"],
    )

    return mappings


_LESSON_MAP: dict[str, LessonKnowledgeMapping] = _build_lesson_map()

_MISTAKE_MAP: list[MistakeKnowledgeMapping] = [
    MistakeKnowledgeMapping(
        error_category="grammar",
        error_type="tense",
        concept_key="past_tense",
        explanation="Use past simple for completed actions in the past.",
        example="I went to the market yesterday.",
        correction="Use past simple: went, not go.",
        lesson_id="grammar-6-past-simple",
    ),
    MistakeKnowledgeMapping(
        error_category="past_tense",
        error_type=None,
        concept_key="past_tense",
        explanation="Use past simple for completed past actions.",
        example="I went to the market yesterday.",
        correction="Change 'go' to 'went' for past time.",
        lesson_id="grammar-6-past-simple",
    ),
    MistakeKnowledgeMapping(
        error_category="grammar",
        error_type="present_perfect",
        concept_key="present_perfect",
        explanation="Present perfect connects past actions to now: have/has + past participle.",
        example="I have visited London twice.",
        correction="Use have/has + past participle, not simple past.",
        lesson_id="grammar-8-present-perfect",
    ),
    MistakeKnowledgeMapping(
        error_category="articles",
        error_type=None,
        concept_key="articles",
        explanation="Use a/an for non-specific nouns; the for specific nouns.",
        example="I saw a dog. The dog was friendly.",
        correction="Check whether the noun is specific or general.",
        lesson_id="grammar-5-articles",
    ),
    MistakeKnowledgeMapping(
        error_category="grammar",
        error_type="articles",
        concept_key="articles",
        explanation="Articles depend on specificity: a/an vs the.",
        example="She is a teacher at the school.",
        correction="Use a before consonant sounds, an before vowel sounds.",
        lesson_id="grammar-5-articles",
    ),
    MistakeKnowledgeMapping(
        error_category="prepositions",
        error_type=None,
        concept_key="prepositions",
        explanation="Common place prepositions: in, on, at.",
        example="I am at school. The book is on the table.",
        correction="Match preposition to place type: at (point), on (surface), in (inside).",
        lesson_id="grammar-7-prepositions",
    ),
    MistakeKnowledgeMapping(
        error_category="grammar",
        error_type="modal",
        concept_key="modal_verbs",
        explanation="Modal verbs express ability, permission, or obligation.",
        example="You should practice every day. She can swim well.",
        correction="Use base verb after modal: should go, not should to go.",
        lesson_id="grammar-9-modal-verbs",
    ),
    MistakeKnowledgeMapping(
        error_category="sentence_structure",
        error_type=None,
        concept_key="sentence_structure",
        explanation="English sentences need subject + verb in correct order.",
        example="I am going to the market.",
        correction="Include subject and correct verb form.",
        lesson_id="grammar-9-relative-clauses",
    ),
    MistakeKnowledgeMapping(
        error_category="grammar",
        error_type="verb_form",
        concept_key="past_tense",
        explanation="After 'am/is/are', use not the base verb for past events.",
        example="I am going (now) vs I went (yesterday).",
        correction="For past completed actions, use past simple not present.",
        lesson_id="grammar-6-past-simple",
    ),
]


def get_concept(key: str) -> KnowledgeConcept | None:
    return _CONCEPTS.get(key)


def get_lesson_mapping(lesson_id: str) -> LessonKnowledgeMapping | None:
    if lesson_id in _LESSON_MAP:
        return _LESSON_MAP[lesson_id]
    lesson = get_lesson(lesson_id)
    if not lesson:
        return None
    meta = lesson.metadata or {}
    grade = meta.get("grade")
    grammar_id = meta.get("grammar_lesson_id")
    if grade and grammar_id:
        lid = f"grammar-{grade}-{grammar_id}"
        return _LESSON_MAP.get(lid)
    scenario = meta.get("scenario")
    if scenario:
        return _LESSON_MAP.get(f"speaking-{scenario}")
    return LessonKnowledgeMapping(
        lesson_id=lesson_id,
        concept_keys=[],
        query_terms=[lesson.title, lesson.skill_focus, lesson.description[:80]],
    )


def get_mistake_mapping(error_category: str, error_type: str | None = None) -> MistakeKnowledgeMapping | None:
    cat = error_category.lower().strip()
    etype = (error_type or "").lower().strip() or None
    for m in _MISTAKE_MAP:
        if m.error_category == cat and (etype is None or m.error_type is None or m.error_type == etype):
            return m
    for m in _MISTAKE_MAP:
        if m.error_category == cat:
            return m
    if cat in _CONCEPTS:
        concept = _CONCEPTS[cat]
        return MistakeKnowledgeMapping(
            error_category=cat,
            error_type=etype,
            concept_key=concept.key,
            explanation=concept.title,
            example="",
            correction="",
            lesson_id=None,
        )
    return None


def find_concepts_by_skill(skill_focus: str) -> list[KnowledgeConcept]:
    skill = skill_focus.lower().strip()
    return [c for c in _CONCEPTS.values() if c.skill_focus == skill or skill in c.skill_focus]


def find_concepts_by_exam(exam: str) -> list[KnowledgeConcept]:
    exam_key = exam.lower().strip()
    return [c for c in _CONCEPTS.values() if c.exam_tag and c.exam_tag == exam_key]


def get_grammar_rule_for_lesson(lesson_id: str) -> str | None:
    mapping = get_lesson_mapping(lesson_id)
    if not mapping or not mapping.grammar_grade or not mapping.grammar_lesson_id:
        return None
    lesson = get_grammar_lesson(mapping.grammar_grade, mapping.grammar_lesson_id)
    return lesson.get("rule") if lesson else None


def list_registry_metadata() -> dict[str, Any]:
    return {
        "concept_count": len(_CONCEPTS),
        "lesson_map_count": len(_LESSON_MAP),
        "mistake_map_count": len(_MISTAKE_MAP),
    }
