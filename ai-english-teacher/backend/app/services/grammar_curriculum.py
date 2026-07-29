"""Grade 5–12 grammar curriculum for school students."""

from __future__ import annotations

GRADE_LEVELS: dict[int, dict[str, str]] = {
    5: {"label": "Grade 5", "age": "10–11", "cefr": "A1"},
    6: {"label": "Grade 6", "age": "11–12", "cefr": "A1"},
    7: {"label": "Grade 7", "age": "12–13", "cefr": "A2"},
    8: {"label": "Grade 8", "age": "13–14", "cefr": "A2"},
    9: {"label": "Grade 9", "age": "14–15", "cefr": "B1"},
    10: {"label": "Grade 10", "age": "15–16", "cefr": "B1"},
    11: {"label": "Grade 11", "age": "16–17", "cefr": "B2"},
    12: {"label": "Grade 12", "age": "17–18", "cefr": "B2"},
}

GRAMMAR_LESSONS: dict[int, list[dict[str, str]]] = {
    5: [
        {"id": "nouns", "title": "Nouns & Pronouns", "rule": "A noun names a person, place, or thing. Use I, you, he, she, it, we, they."},
        {"id": "verbs-present", "title": "Present Simple Verbs", "rule": "Use present simple for habits: I play, she plays (add -s for he/she/it)."},
        {"id": "articles", "title": "A, An, The", "rule": "Use 'a' before consonant sounds, 'an' before vowel sounds, 'the' for specific things."},
    ],
    6: [
        {"id": "past-simple", "title": "Past Simple", "rule": "Regular verbs: add -ed (walked). Irregular: go → went, eat → ate."},
        {"id": "adjectives", "title": "Adjectives", "rule": "Adjectives describe nouns. Order: opinion before size (a nice big dog)."},
        {"id": "questions", "title": "Question Words", "rule": "Who, what, where, when, why, how — put auxiliary before subject: Do you like...?"},
    ],
    7: [
        {"id": "present-continuous", "title": "Present Continuous", "rule": "am/is/are + -ing for actions happening now: She is reading."},
        {"id": "prepositions", "title": "Prepositions of Place", "rule": "in, on, at, under, behind — in the box, on the table, at school."},
        {"id": "comparatives", "title": "Comparatives", "rule": "Short adjectives: add -er (taller). Long: more + adjective (more beautiful)."},
    ],
    8: [
        {"id": "present-perfect", "title": "Present Perfect", "rule": "have/has + past participle for life experience: I have visited London."},
        {"id": "passive", "title": "Passive Voice", "rule": "be + past participle: The cake was baked by Mom."},
        {"id": "reported-speech", "title": "Reported Speech", "rule": "Shift tense back: He said, 'I am tired' → He said he was tired."},
    ],
    9: [
        {"id": "conditionals-1", "title": "First Conditional", "rule": "If + present, will + verb: If it rains, we will stay home."},
        {"id": "relative-clauses", "title": "Relative Clauses", "rule": "who for people, which for things, where for places."},
        {"id": "modal-verbs", "title": "Modal Verbs", "rule": "can, could, must, should, may — express ability, permission, obligation."},
    ],
    10: [
        {"id": "conditionals-2", "title": "Second Conditional", "rule": "If + past, would + verb: If I were rich, I would travel."},
        {"id": "gerunds-infinitives", "title": "Gerunds & Infinitives", "rule": "enjoy + -ing; want + to + verb. Some verbs take both with different meanings."},
        {"id": "essay-connectors", "title": "Linking Words", "rule": "However, therefore, although, moreover — connect ideas in writing and speech."},
    ],
    11: [
        {"id": "perfect-continuous", "title": "Perfect Continuous", "rule": "have been + -ing: I have been studying for two hours."},
        {"id": "inversion", "title": "Inversion", "rule": "Never have I seen... — auxiliary before subject for emphasis."},
        {"id": "advanced-passive", "title": "Advanced Passive", "rule": "It is said that..., He is believed to have..."},
    ],
    12: [
        {"id": "subjunctive", "title": "Subjunctive Mood", "rule": "I suggest that he study harder (base verb, no -s)."},
        {"id": "cleft-sentences", "title": "Cleft Sentences", "rule": "It was John who called. What I need is time."},
        {"id": "academic-style", "title": "Academic Grammar", "rule": "Formal register: avoid contractions, use passive and nominalisation where appropriate."},
    ],
}


def get_grade_info(grade: int) -> dict[str, str] | None:
    return GRADE_LEVELS.get(grade)


def get_lessons_for_grade(grade: int) -> list[dict[str, str]]:
    return GRAMMAR_LESSONS.get(grade, [])


def get_lesson(grade: int, lesson_id: str) -> dict[str, str] | None:
    for lesson in get_lessons_for_grade(grade):
        if lesson["id"] == lesson_id:
            return lesson
    return None
