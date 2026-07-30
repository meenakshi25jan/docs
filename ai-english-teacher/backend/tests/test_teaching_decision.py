"""Tests for teaching decision engine and voice turn helpers."""

import pytest

from app.orchestration.voice.teaching_decision import decide_teaching_mode, build_teaching_instruction


class TestTeachingDecision:
    def test_no_errors_returns_none(self):
        result = decide_teaching_mode(
            grammar_errors=[],
            fluency_score=80,
            persona_correction_style="delayed",
            turn_count=1,
            pending_corrections=[],
            student_message_length=10,
        )
        assert result["teaching_mode"] == "none"

    def test_immediate_for_high_severity(self):
        errors = [{"text": "he go", "correction": "he goes", "severity": "high", "category": "grammar"}]
        result = decide_teaching_mode(
            grammar_errors=errors,
            fluency_score=75,
            persona_correction_style="delayed",
            turn_count=1,
            pending_corrections=[],
            student_message_length=5,
        )
        assert result["teaching_mode"] == "immediate"
        assert result["corrections_now"]

    def test_socratic_persona(self):
        errors = [{"text": "I goed", "correction": "I went", "severity": "medium", "category": "tense"}]
        result = decide_teaching_mode(
            grammar_errors=errors,
            fluency_score=75,
            persona_correction_style="socratic",
            turn_count=1,
            pending_corrections=[],
            student_message_length=5,
        )
        assert result["teaching_mode"] == "socratic"

    def test_delayed_for_long_speech(self):
        errors = [{"text": "a error", "correction": "an error", "severity": "low", "category": "articles"}]
        result = decide_teaching_mode(
            grammar_errors=errors,
            fluency_score=75,
            persona_correction_style="delayed",
            turn_count=2,
            pending_corrections=[],
            student_message_length=50,
        )
        assert result["teaching_mode"] == "delayed"
        assert result["reason"] == "extended_speech_batch"

    def test_build_instruction_immediate(self):
        decision = {
            "teaching_mode": "immediate",
            "corrections_now": [{"wrong": "he go", "correct": "he goes"}],
        }
        text = build_teaching_instruction(decision)
        assert "IMMEDIATE" in text
        assert "he goes" in text


class TestPersonas:
    def test_list_personas(self):
        from app.orchestration.personas import list_personas, get_persona, list_scenarios

        personas = list_personas()
        assert len(personas) >= 5
        assert get_persona("ielts_examiner")["label"] == "IELTS Examiner"
        scenarios = list_scenarios()
        assert any(s["id"] == "job_interview" for s in scenarios)
