"""Tests for Wave 2 voice agents and Wave 1 services."""

import pytest

from app.orchestration.voice.fluency_agent import analyze_fluency
from app.orchestration.voice.pronunciation_agent import analyze_pronunciation
from app.orchestration.voice.speech_quality_agent import analyze_speech_quality
from app.services.curriculum_data import tokenize


class TestFluencyAgent:
    def test_smooth_speech_scores_high(self):
        result = analyze_fluency(
            "I have been working here for five years and I really enjoy my job.",
            duration_seconds=8.0,
        )
        assert result["fluency"] >= 70
        assert result["wpm"] is not None

    def test_fillers_lower_score(self):
        result = analyze_fluency("Um, I, uh, like, you know, went to the store.")
        assert result["fillers"] >= 2
        assert result["fluency"] < 85


class TestPronunciationAgent:
    def test_detects_grammar_issue(self):
        result = analyze_pronunciation("Yesterday he go to the market.")
        assert result["phoneme_score"] < 82
        assert result["issues"]


class TestSpeechQuality:
    def test_noisy_audio_flagged(self):
        result = analyze_speech_quality({"snr_db": 8})
        assert result["quality"] == "poor"
        assert "background_noise" in result["issues"]


class TestCurriculumData:
    def test_tokenize(self):
        tokens = tokenize("Explain present perfect tense")
        assert "explain" in tokens
        assert "present" in tokens
