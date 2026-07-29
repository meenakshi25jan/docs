from app.services.grammar_curriculum import get_lesson, get_lessons_for_grade


def test_all_grades_have_lessons():
    for grade in range(5, 13):
        lessons = get_lessons_for_grade(grade)
        assert len(lessons) >= 3
        assert get_lesson(grade, lessons[0]["id"]) is not None


def test_unknown_lesson():
    assert get_lesson(5, "missing") is None
