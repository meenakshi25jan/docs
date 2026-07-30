"""Knowledge Intelligence v1 — unified retrieval and grounding."""

from __future__ import annotations

import logging
import re
from typing import Any

from app.schemas.knowledge_intelligence import (
    GroundingContext,
    GroundingValidation,
    KnowledgeChunkResult,
    KnowledgeGroundingMetadata,
    KnowledgeSearchResponse,
    LessonContextResponse,
    MistakeContextResponse,
)
from app.services.curriculum_data import CURRICULUM_SNIPPETS, tokenize
from app.services.curriculum_registry import get_lesson
from app.services.knowledge_registry import (
    find_concepts_by_exam,
    find_concepts_by_skill,
    get_concept,
    get_grammar_rule_for_lesson,
    get_lesson_mapping,
    get_mistake_mapping,
)
from app.services.knowledge_store import retrieve_knowledge

logger = logging.getLogger(__name__)

MAX_GROUNDING_CHARS = 800
MAX_EXAMPLES = 2
MAX_PRACTICE_PROMPTS = 1
MAX_CHUNKS = 3
MIN_RELEVANCE_SCORE = 0.15
MIN_KEYWORD_OVERLAP = 1

CEFR_ORDER = {"A1": 0, "A2": 1, "B1": 2, "B2": 3, "C1": 4, "C2": 5}

SOURCE_QUALITY: dict[str, float] = {
    "grammar_curriculum": 1.0,
    "knowledge_chunks": 0.85,
    "curriculum_registry": 0.75,
    "keyword": 0.6,
}

RANK_WEIGHTS = {
    "retrieval": 0.35,
    "lesson": 0.25,
    "concept": 0.15,
    "skill": 0.10,
    "mistake": 0.10,
    "cefr": 0.05,
}


def _cefr_index(level: str | None) -> int:
    if not level:
        return 2
    return CEFR_ORDER.get(level.upper(), 2)


def _sanitize_voice_text(text: str) -> str:
    text = re.sub(r"[#*_`]", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def _truncate_sentences(text: str, max_chars: int) -> str:
    text = _sanitize_voice_text(text)
    if len(text) <= max_chars:
        return text
    cut = text[:max_chars]
    last_period = cut.rfind(".")
    if last_period > max_chars // 2:
        return cut[:last_period + 1].strip()
    return cut.rstrip() + "..."


def _chunk_from_dict(
    data: dict[str, Any],
    *,
    source_type: str,
    lesson_match: bool = False,
    concept_match: bool = False,
    skill_match: bool = False,
    mistake_match: bool = False,
    cefr_level: str | None = None,
) -> dict[str, Any]:
    return {
        "text": data.get("text", ""),
        "source": data.get("source", source_type),
        "topic": data.get("topic", ""),
        "score": float(data.get("score", 0.5)),
        "method": data.get("method", source_type),
        "source_type": source_type,
        "lesson_match": lesson_match,
        "concept_match": concept_match,
        "skill_match": skill_match,
        "mistake_match": mistake_match,
        "cefr_level": cefr_level,
    }


def _grammar_rule_candidate(lesson_id: str) -> dict[str, Any] | None:
    rule = get_grammar_rule_for_lesson(lesson_id)
    if not rule:
        return None
    lesson = get_lesson(lesson_id)
    title = lesson.title if lesson else lesson_id
    return _chunk_from_dict(
        {
            "text": rule,
            "source": f"Grammar: {title}",
            "topic": lesson_id,
            "score": 0.95,
            "method": "grammar_curriculum",
        },
        source_type="grammar_curriculum",
        lesson_match=True,
        concept_match=True,
    )


def _registry_description_candidate(lesson_id: str) -> dict[str, Any] | None:
    lesson = get_lesson(lesson_id)
    if not lesson or not lesson.description:
        return None
    return _chunk_from_dict(
        {
            "text": lesson.description,
            "source": f"Lesson: {lesson.title}",
            "topic": lesson.lesson_id,
            "score": 0.7,
            "method": "curriculum_registry",
        },
        source_type="curriculum_registry",
        lesson_match=True,
        skill_match=True,
    )


def _mistake_candidate(mapping) -> dict[str, Any]:
    parts = [mapping.explanation]
    if mapping.example:
        parts.append(f"Example: {mapping.example}")
    text = " ".join(parts)
    return _chunk_from_dict(
        {
            "text": text,
            "source": f"Mistake: {mapping.error_category}",
            "topic": mapping.concept_key,
            "score": 0.9,
            "method": "mistake_map",
        },
        source_type="grammar_curriculum",
        mistake_match=True,
        concept_match=True,
    )


def _expand_query(
    message: str,
    *,
    lesson_id: str | None = None,
    skill_focus: str | None = None,
    scenario: str = "",
    mistake_categories: list[str] | None = None,
    target_exam: str | None = None,
) -> str:
    terms: list[str] = [message]
    if lesson_id:
        mapping = get_lesson_mapping(lesson_id)
        if mapping:
            terms.extend(mapping.query_terms[:3])
            for ck in mapping.concept_keys:
                concept = get_concept(ck)
                if concept:
                    terms.extend(concept.query_terms[:2])
        lesson = get_lesson(lesson_id)
        if lesson:
            terms.append(lesson.title)
    if skill_focus:
        terms.append(skill_focus)
        for concept in find_concepts_by_skill(skill_focus):
            terms.extend(concept.query_terms[:2])
    if scenario:
        terms.append(scenario.replace("_", " "))
    if mistake_categories:
        for cat in mistake_categories[:3]:
            m = get_mistake_mapping(cat)
            if m:
                terms.append(m.concept_key.replace("_", " "))
    if target_exam:
        for concept in find_concepts_by_exam(target_exam):
            terms.extend(concept.query_terms[:2])
    return " ".join(t for t in terms if t).strip()


def _rank_chunks(
    candidates: list[dict[str, Any]],
    *,
    lesson_id: str | None = None,
    skill_focus: str | None = None,
    cefr_level: str | None = None,
    mistake_categories: list[str] | None = None,
) -> list[dict[str, Any]]:
    learner_cefr = _cefr_index(cefr_level)
    lesson_concepts: set[str] = set()
    if lesson_id:
        mapping = get_lesson_mapping(lesson_id)
        if mapping:
            lesson_concepts = set(mapping.concept_keys)

    scored: list[tuple[float, dict[str, Any]]] = []
    for c in candidates:
        text = (c.get("text") or "").strip()
        if not text:
            continue

        retrieval_score = float(c.get("score", 0.0))
        source_type = c.get("source_type", "keyword")
        quality = SOURCE_QUALITY.get(source_type, 0.5)
        retrieval_component = retrieval_score * quality

        lesson_component = 1.0 if c.get("lesson_match") else (0.5 if lesson_id and c.get("topic") == lesson_id else 0.0)
        concept_component = 1.0 if c.get("concept_match") else 0.0
        if not concept_component and lesson_concepts and c.get("topic") in lesson_concepts:
            concept_component = 0.8

        skill_component = 1.0 if c.get("skill_match") or (
            skill_focus and skill_focus.lower() in text.lower()
        ) else 0.0

        mistake_component = 1.0 if c.get("mistake_match") else 0.0
        if not mistake_component and mistake_categories:
            for cat in mistake_categories:
                if cat.lower() in text.lower():
                    mistake_component = 0.7
                    break

        chunk_cefr = _cefr_index(c.get("cefr_level"))
        cefr_diff = abs(chunk_cefr - learner_cefr)
        cefr_component = 1.0 if cefr_diff <= 1 else (0.3 if cefr_diff == 2 else 0.0)

        brevity = max(0.0, 1.0 - len(text) / 500.0)

        final = (
            RANK_WEIGHTS["retrieval"] * retrieval_component
            + RANK_WEIGHTS["lesson"] * lesson_component
            + RANK_WEIGHTS["concept"] * concept_component
            + RANK_WEIGHTS["skill"] * skill_component
            + RANK_WEIGHTS["mistake"] * mistake_component
            + RANK_WEIGHTS["cefr"] * cefr_component
            + 0.05 * brevity
        )
        scored.append((final, c))

    scored.sort(key=lambda x: x[0], reverse=True)
    return [c for _, c in scored]


def _validate_chunks(chunks: list[dict[str, Any]], query: str) -> tuple[list[dict[str, Any]], GroundingValidation]:
    query_tokens = tokenize(query)
    valid: list[dict[str, Any]] = []
    methods: set[str] = set()

    for c in chunks:
        text = (c.get("text") or "").strip()
        if not text:
            continue
        method = c.get("method", c.get("source_type", "keyword"))
        score = float(c.get("score", 0))
        if method == "pgvector" and score < MIN_RELEVANCE_SCORE:
            continue
        if method in ("keyword", "keyword_fallback") and query_tokens:
            overlap = len(query_tokens & tokenize(text + " " + c.get("topic", "")))
            if overlap < MIN_KEYWORD_OVERLAP and score < 0.5:
                continue
        if not c.get("source") and not c.get("topic"):
            continue
        valid.append(c)
        methods.add(method)

    fallback_used = not any(m == "pgvector" for m in methods) and bool(valid)
    retrieval_method = "pgvector" if "pgvector" in methods else ("keyword" if valid else "none")

    validation = GroundingValidation(
        relevance_ok=bool(valid),
        size_ok=True,
        voice_ok=True,
        fallback_used=fallback_used,
        retrieval_method=retrieval_method,
        chunk_count=len(valid),
    )
    return valid, validation


def _build_compact_grounding(
    chunks: list[dict[str, Any]],
    validation: GroundingValidation,
    *,
    lesson_id: str | None = None,
    skill_focus: str | None = None,
    cefr_level: str | None = None,
    practice_prompts: list[str] | None = None,
) -> GroundingContext:
    explanations: list[str] = []
    examples: list[str] = []
    sources: list[str] = []
    lines: list[str] = []

    for c in chunks[:MAX_CHUNKS]:
        text = _truncate_sentences(c.get("text", ""), 280)
        if not text:
            continue
        source_type = c.get("source_type", "knowledge_chunks")
        if source_type not in sources:
            sources.append(source_type)
        explanations.append(text)
        lines.append(text)

    prompts = list(practice_prompts or [])[:MAX_PRACTICE_PROMPTS]

    for c in chunks:
        if len(examples) >= MAX_EXAMPLES:
            break
        ex_match = re.search(r"Example:\s*(.+?)(?:\.|$)", c.get("text", ""), re.I)
        if ex_match:
            examples.append(_truncate_sentences(ex_match.group(1), 120))

    compact = _truncate_sentences(" ".join(lines), MAX_GROUNDING_CHARS)
    size_ok = len(compact) <= MAX_GROUNDING_CHARS
    validation.size_ok = size_ok
    validation.voice_ok = bool(compact) and "\n\n" not in compact

    return GroundingContext(
        compact_text=compact,
        explanations=explanations[:MAX_CHUNKS],
        examples=examples[:MAX_EXAMPLES],
        practice_prompts=prompts,
        sources=sources,
        lesson_id=lesson_id,
        skill_focus=skill_focus,
        cefr_level=cefr_level,
        validation=validation,
        metadata={"line_count": len(explanations)},
    )


def _to_chunk_results(chunks: list[dict[str, Any]]) -> list[KnowledgeChunkResult]:
    return [
        KnowledgeChunkResult(
            text=c.get("text", ""),
            source=c.get("source", ""),
            topic=c.get("topic"),
            score=float(c.get("score", 0)),
            method=c.get("method", "keyword"),
            source_type=c.get("source_type", "knowledge_chunks"),
        )
        for c in chunks
    ]


class KnowledgeIntelligenceService:
    async def _collect_candidates(
        self,
        *,
        message: str,
        lesson_id: str | None = None,
        skill_focus: str | None = None,
        scenario: str = "",
        cefr_level: str | None = None,
        target_exam: str | None = None,
        mistake_categories: list[str] | None = None,
        tenant_id: str | None = None,
        top_k: int = 5,
    ) -> list[dict[str, Any]]:
        candidates: list[dict[str, Any]] = []

        if lesson_id:
            gr = _grammar_rule_candidate(lesson_id)
            if gr:
                candidates.append(gr)
            reg = _registry_description_candidate(lesson_id)
            if reg:
                candidates.append(reg)

        if mistake_categories:
            for cat in mistake_categories[:3]:
                m = get_mistake_mapping(cat)
                if m:
                    candidates.append(_mistake_candidate(m))

        expanded = _expand_query(
            message,
            lesson_id=lesson_id,
            skill_focus=skill_focus,
            scenario=scenario,
            mistake_categories=mistake_categories,
            target_exam=target_exam,
        )

        rag_chunks = await retrieve_knowledge(
            expanded or message,
            scenario=scenario,
            tenant_id=tenant_id,
            top_k=top_k,
        )
        for rc in rag_chunks:
            method = rc.get("method", "keyword")
            source_type = "knowledge_chunks" if method == "pgvector" else "keyword"
            candidates.append(
                _chunk_from_dict(rc, source_type=source_type, skill_match=bool(skill_focus))
            )

        if not rag_chunks and expanded:
            query_tokens = tokenize(expanded)
            for snippet in CURRICULUM_SNIPPETS:
                topic_tokens = tokenize(snippet["topic"])
                text_tokens = tokenize(snippet["text"])
                overlap = len(query_tokens & (topic_tokens | text_tokens))
                if overlap > 0:
                    candidates.append(
                        _chunk_from_dict(
                            {
                                "text": snippet["text"],
                                "source": snippet["source"],
                                "topic": snippet["topic"],
                                "score": overlap / max(len(query_tokens), 1),
                                "method": "keyword",
                            },
                            source_type="keyword",
                            concept_match=True,
                        )
                    )

        return candidates

    async def build_lesson_context(
        self,
        lesson_id: str,
        *,
        cefr_level: str | None = None,
        target_exam: str | None = None,
        tenant_id: str | None = None,
    ) -> LessonContextResponse:
        lesson = get_lesson(lesson_id)
        skill_focus = lesson.skill_focus if lesson else None
        message = lesson.title if lesson else lesson_id

        candidates = await self._collect_candidates(
            message=message,
            lesson_id=lesson_id,
            skill_focus=skill_focus,
            cefr_level=cefr_level or (lesson.cefr_level if lesson else None),
            target_exam=target_exam,
            tenant_id=tenant_id,
            top_k=5,
        )
        ranked = _rank_chunks(
            candidates,
            lesson_id=lesson_id,
            skill_focus=skill_focus,
            cefr_level=cefr_level,
        )
        valid, validation = _validate_chunks(ranked, message)
        grounding = _build_compact_grounding(
            valid,
            validation,
            lesson_id=lesson_id,
            skill_focus=skill_focus,
            cefr_level=cefr_level or (lesson.cefr_level if lesson else None),
        )
        return LessonContextResponse(
            lesson_id=lesson_id,
            grounding=grounding,
            chunks=_to_chunk_results(valid[:MAX_CHUNKS]),
        )

    async def build_mistake_context(
        self,
        error_category: str,
        *,
        error_type: str | None = None,
        error_text: str | None = None,
        cefr_level: str | None = None,
        tenant_id: str | None = None,
    ) -> MistakeContextResponse:
        mapping = get_mistake_mapping(error_category, error_type)
        message = error_text or error_category
        mistake_cats = [error_category]
        lesson_id = mapping.lesson_id if mapping else None

        candidates: list[dict[str, Any]] = []
        if mapping:
            candidates.append(_mistake_candidate(mapping))

        extra = await self._collect_candidates(
            message=message,
            lesson_id=lesson_id,
            cefr_level=cefr_level,
            mistake_categories=mistake_cats,
            tenant_id=tenant_id,
            top_k=5,
        )
        candidates.extend(extra)

        ranked = _rank_chunks(
            candidates,
            lesson_id=lesson_id,
            cefr_level=cefr_level,
            mistake_categories=mistake_cats,
        )
        valid, validation = _validate_chunks(ranked, message)
        skill = get_concept(mapping.concept_key).skill_focus if mapping and get_concept(mapping.concept_key) else "grammar"
        grounding = _build_compact_grounding(
            valid,
            validation,
            lesson_id=lesson_id,
            skill_focus=skill,
            cefr_level=cefr_level,
        )
        return MistakeContextResponse(
            error_category=error_category,
            error_type=error_type,
            grounding=grounding,
            chunks=_to_chunk_results(valid[:MAX_CHUNKS]),
        )

    async def search(
        self,
        query: str,
        *,
        skill_focus: str | None = None,
        lesson_id: str | None = None,
        cefr_level: str | None = None,
        target_exam: str | None = None,
        tenant_id: str | None = None,
        top_k: int = 5,
    ) -> KnowledgeSearchResponse:
        candidates = await self._collect_candidates(
            message=query,
            lesson_id=lesson_id,
            skill_focus=skill_focus,
            cefr_level=cefr_level,
            target_exam=target_exam,
            tenant_id=tenant_id,
            top_k=top_k,
        )
        ranked = _rank_chunks(
            candidates,
            lesson_id=lesson_id,
            skill_focus=skill_focus,
            cefr_level=cefr_level,
        )
        valid, validation = _validate_chunks(ranked, query)
        grounding = _build_compact_grounding(
            valid,
            validation,
            lesson_id=lesson_id,
            skill_focus=skill_focus,
            cefr_level=cefr_level,
        )
        return KnowledgeSearchResponse(
            query=query,
            chunks=_to_chunk_results(valid[:MAX_CHUNKS]),
            grounding=grounding,
        )

    async def build_grounding_context(
        self,
        *,
        message: str,
        scenario: str = "",
        lesson_id: str | None = None,
        skill_focus: str | None = None,
        cefr_level: str | None = None,
        target_exam: str | None = None,
        recurring_mistakes: list[Any] | None = None,
        tenant_id: str | None = None,
        retrieve: bool = True,
    ) -> GroundingContext:
        if not retrieve or not message.strip():
            return GroundingContext(
                validation=GroundingValidation(
                    relevance_ok=False,
                    retrieval_method="none",
                    chunk_count=0,
                    fallback_used=True,
                )
            )

        mistake_categories: list[str] = []
        if recurring_mistakes:
            for m in recurring_mistakes[:5]:
                if isinstance(m, dict):
                    cat = m.get("error_category") or m.get("mistake_type") or m.get("category")
                    if cat:
                        mistake_categories.append(str(cat))
                elif isinstance(m, str):
                    mistake_categories.append(m)

        try:
            candidates = await self._collect_candidates(
                message=message,
                lesson_id=lesson_id,
                skill_focus=skill_focus,
                scenario=scenario,
                cefr_level=cefr_level,
                target_exam=target_exam,
                mistake_categories=mistake_categories,
                tenant_id=tenant_id,
                top_k=5,
            )
            ranked = _rank_chunks(
                candidates,
                lesson_id=lesson_id,
                skill_focus=skill_focus,
                cefr_level=cefr_level,
                mistake_categories=mistake_categories,
            )
            valid, validation = _validate_chunks(ranked, message)
            return _build_compact_grounding(
                valid,
                validation,
                lesson_id=lesson_id,
                skill_focus=skill_focus,
                cefr_level=cefr_level,
            )
        except Exception as exc:  # noqa: BLE001
            logger.warning("knowledge_intelligence.grounding_failed", extra={"error": str(exc)})
            return GroundingContext(
                validation=GroundingValidation(
                    relevance_ok=False,
                    size_ok=True,
                    voice_ok=True,
                    fallback_used=True,
                    retrieval_method="error",
                    chunk_count=0,
                )
            )

    def grounding_to_knowledge_context(self, grounding: GroundingContext) -> str:
        if not grounding.explanations:
            return ""
        lines = [f"- [{s}] {t}" for s, t in zip(grounding.sources or ["curriculum"], grounding.explanations)]
        return "\n".join(lines[:MAX_CHUNKS])

    def to_metadata(self, grounding: GroundingContext) -> KnowledgeGroundingMetadata:
        return KnowledgeGroundingMetadata(
            lesson_id=grounding.lesson_id,
            skill_focus=grounding.skill_focus,
            chunk_count=grounding.validation.chunk_count,
            sources=grounding.sources,
            fallback_used=grounding.validation.fallback_used,
        )

    def inject_teaching_instruction(
        self,
        teaching_instruction: str,
        grounding: GroundingContext | Any,
    ) -> str:
        compact = (
            grounding.compact_text
            if hasattr(grounding, "compact_text")
            else str(grounding)
        )
        if not compact:
            return teaching_instruction or ""
        block = f"Teaching knowledge:\n{compact}"
        base = (teaching_instruction or "").strip()
        if block in base:
            return base
        return f"{base}\n{block}".strip() if base else block
