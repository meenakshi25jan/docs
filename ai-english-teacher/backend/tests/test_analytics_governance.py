"""Governance analytics tests."""

from uuid import uuid4

from app.services.analytics_service import AnalyticsService


class TestGovernanceAnalytics:
    def setup_method(self):
        self.service = AnalyticsService()

    def test_governance_score_aggregation(self):
        messages = [
            {
                "governance": {
                    "teacher_response_score": 0.9,
                    "grounding_score": 0.8,
                    "curriculum_score": 0.85,
                    "memory_score": 0.75,
                    "overall_score": 0.82,
                    "warnings": [],
                    "status": "good",
                },
            },
            {
                "governance": {
                    "teacher_response_score": 0.7,
                    "grounding_score": 0.6,
                    "curriculum_score": 0.65,
                    "memory_score": 0.7,
                    "overall_score": 0.68,
                    "warnings": ["missing_practice_prompt"],
                    "status": "fair",
                },
            },
        ]
        result = self.service._aggregate_governance_from_messages(messages, uuid4())
        assert result.has_data
        assert result.evaluation_count == 2
        assert result.avg_teacher_response_score == 0.8
        assert result.avg_overall_score == 0.75
        assert result.status_breakdown["good"] == 1
        assert result.status_breakdown["fair"] == 1

    def test_governance_warning_count(self):
        messages = [
            {"governance": {"overall_score": 0.5, "warnings": ["ungrounded_teaching", "excessive_response_length"], "status": "needs_attention"}},
        ]
        result = self.service._aggregate_governance_from_messages(messages, uuid4())
        assert result.warning_count == 2
        assert result.warning_frequency["ungrounded_teaching"] == 1

    def test_empty_governance_safe(self):
        result = self.service._aggregate_governance_from_messages([], uuid4())
        assert not result.has_data
        assert result.evaluation_count == 0
