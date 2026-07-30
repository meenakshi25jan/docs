"""Tests for knowledge validation."""

from app.schemas.knowledge_intelligence import GroundingValidation
from app.services.knowledge_intelligence_service import (
    MAX_GROUNDING_CHARS,
    _build_compact_grounding,
    _validate_chunks,
)


class TestKnowledgeValidation:
    def test_reject_empty_chunks(self):
        valid, validation = _validate_chunks([], "test query")
        assert valid == []
        assert validation.chunk_count == 0

    def test_grounding_size_limits(self):
        long_text = "Word " * 300
        chunks = [
            {
                "text": long_text,
                "source": "test",
                "topic": "test",
                "score": 0.9,
                "method": "keyword",
                "source_type": "keyword",
            }
        ]
        validation = GroundingValidation(relevance_ok=True, retrieval_method="keyword", chunk_count=1)
        grounding = _build_compact_grounding(chunks, validation)
        assert len(grounding.compact_text) <= MAX_GROUNDING_CHARS + 20

    def test_max_examples_limit(self):
        chunks = [
            {
                "text": "Rule one. Example: I went home.",
                "source": "a",
                "topic": "past",
                "score": 0.9,
                "method": "keyword",
                "source_type": "grammar_curriculum",
            },
            {
                "text": "Rule two. Example: She ate lunch.",
                "source": "b",
                "topic": "past",
                "score": 0.8,
                "method": "keyword",
                "source_type": "grammar_curriculum",
            },
            {
                "text": "Rule three. Example: They ran fast.",
                "source": "c",
                "topic": "past",
                "score": 0.7,
                "method": "keyword",
                "source_type": "grammar_curriculum",
            },
        ]
        validation = GroundingValidation(relevance_ok=True, retrieval_method="keyword", chunk_count=3)
        grounding = _build_compact_grounding(chunks, validation)
        assert len(grounding.examples) <= 2

    def test_sanitize_voice_text(self):
        from app.services.knowledge_intelligence_service import _sanitize_voice_text

        assert "#" not in _sanitize_voice_text("**Bold** rule here.")
