"""Tests for curriculum registry."""

from app.services.curriculum_registry import (
    get_lesson,
    get_lessons,
    get_path,
    get_paths,
    get_skills,
    get_topics,
    get_next_cefr_lesson,
    TOPIC_IDS,
)


class TestCurriculumRegistry:
    def test_topics_include_required_ids(self):
        ids = {t.id for t in get_topics()}
        for topic in TOPIC_IDS:
            assert topic in ids

    def test_skills_for_grammar_topic(self):
        skills = get_skills("grammar")
        assert len(skills) >= 1
        assert skills[0].topic_id == "grammar"

    def test_grammar_lessons_exist(self):
        lessons = get_lessons(topic_id="grammar")
        assert len(lessons) >= 10
        assert all(l.lesson_id.startswith("grammar-") for l in lessons)

    def test_get_lesson_placement(self):
        lesson = get_lesson("placement-assessment")
        assert lesson is not None
        assert lesson.route == "/assessment"

    def test_exam_lessons_exist(self):
        assert get_lesson("exam-ielts-examiner") is not None
        assert get_lesson("exam-pte-coach") is not None

    def test_speaking_scenarios_registered(self):
        speaking = get_lessons(topic_id="speaking")
        assert any(l.lesson_id == "speaking-restaurant" for l in speaking)

    def test_learning_paths(self):
        paths = get_paths()
        ids = {p.path_id for p in paths}
        assert "daily" in ids
        assert "weekly" in ids
        assert "exam" in ids
        assert "repair" in ids
        assert "confidence" in ids

    def test_get_path_daily(self):
        path = get_path("daily")
        assert path is not None
        assert path.path_id == "daily"

    def test_next_cefr_lesson_skips_completed(self):
        completed = {"grammar-9-conditionals-1"}
        lesson = get_next_cefr_lesson("B1", completed)
        assert lesson is not None
        assert lesson.lesson_id not in completed
