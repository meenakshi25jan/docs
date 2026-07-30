"""Knowledge Intelligence API schemas."""

from typing import Any

from pydantic import BaseModel, Field


class KnowledgeSourceInfo(BaseModel):
    source_type: str
    label: str
    topic: str | None = None
    score: float = 0.0


class KnowledgeChunkResult(BaseModel):
    text: str
    source: str
    topic: str | None = None
    score: float = 0.0
    method: str = "keyword"
    source_type: str = "knowledge_chunks"


class GroundingValidation(BaseModel):
    relevance_ok: bool = True
    size_ok: bool = True
    voice_ok: bool = True
    fallback_used: bool = False
    retrieval_method: str = "none"
    chunk_count: int = 0


class GroundingContext(BaseModel):
    compact_text: str = ""
    explanations: list[str] = Field(default_factory=list)
    examples: list[str] = Field(default_factory=list)
    practice_prompts: list[str] = Field(default_factory=list)
    sources: list[str] = Field(default_factory=list)
    lesson_id: str | None = None
    skill_focus: str | None = None
    cefr_level: str | None = None
    validation: GroundingValidation = Field(default_factory=GroundingValidation)
    metadata: dict[str, Any] = Field(default_factory=dict)


class KnowledgeGroundingMetadata(BaseModel):
    lesson_id: str | None = None
    skill_focus: str | None = None
    chunk_count: int = 0
    sources: list[str] = Field(default_factory=list)
    fallback_used: bool = False


class LessonContextResponse(BaseModel):
    lesson_id: str
    grounding: GroundingContext
    chunks: list[KnowledgeChunkResult] = Field(default_factory=list)


class MistakeContextResponse(BaseModel):
    error_category: str
    error_type: str | None = None
    grounding: GroundingContext
    chunks: list[KnowledgeChunkResult] = Field(default_factory=list)


class KnowledgeSearchResponse(BaseModel):
    query: str
    chunks: list[KnowledgeChunkResult] = Field(default_factory=list)
    grounding: GroundingContext
