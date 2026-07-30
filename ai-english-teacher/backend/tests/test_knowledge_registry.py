"""Tests for knowledge registry."""

from app.services.knowledge_registry import (
    find_concepts_by_exam,
    find_concepts_by_skill,
    get_concept,
    get_lesson_mapping,
    get_mistake_mapping,
    list_registry_metadata,
)


class TestKnowledgeRegistry:
    def test_lesson_mapping_grammar(self):
        m = get_lesson_mapping("grammar-9-modal-verbs")
        assert m is not None
        assert "modal_verbs" in m.concept_keys

    def test_lesson_mapping_speaking(self):
        m = get_lesson_mapping("speaking-restaurant")
        assert m is not None
        assert "restaurant_roleplay" in m.concept_keys

    def test_mistake_mapping_past_tense(self):
        m = get_mistake_mapping("past_tense")
        assert m is not None
        assert m.concept_key == "past_tense"
        assert "yesterday" in m.example.lower() or "went" in m.example.lower()

    def test_get_concept_present_perfect(self):
        c = get_concept("present_perfect")
        assert c is not None
        assert c.skill_focus == "grammar"

    def test_find_concepts_by_skill(self):
        concepts = find_concepts_by_skill("grammar")
        assert len(concepts) >= 3

    def test_find_concepts_by_exam_ielts(self):
        concepts = find_concepts_by_exam("ielts")
        assert any(c.key == "ielts_speaking" for c in concepts)

    def test_registry_metadata(self):
        meta = list_registry_metadata()
        assert meta["concept_count"] >= 10
        assert meta["lesson_map_count"] > 0
