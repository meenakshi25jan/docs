"""Progress analytics tests."""

from datetime import datetime, timezone

from app.services.analytics_service import (
    AnalyticsService,
    _build_skill_trend_from_values,
    trend_from_delta,
)


class TestTrendCalculation:
    def test_improving_trend(self):
        assert trend_from_delta(5.0) == "improving"

    def test_declining_trend(self):
        assert trend_from_delta(-5.0) == "declining"

    def test_stable_trend(self):
        assert trend_from_delta(1.0) == "stable"
        assert trend_from_delta(None) == "stable"

    def test_skill_trend_improving(self):
        now = datetime.now(timezone.utc)
        later = datetime.now(timezone.utc)
        trend = _build_skill_trend_from_values(
            "grammar",
            [(now, 60.0), (later, 70.0)],
        )
        assert trend.trend == "improving"
        assert trend.delta == 10.0

    def test_skill_trend_declining(self):
        now = datetime.now(timezone.utc)
        later = datetime.now(timezone.utc)
        trend = _build_skill_trend_from_values(
            "grammar",
            [(now, 80.0), (later, 70.0)],
        )
        assert trend.trend == "declining"

    def test_empty_progress_safe_defaults(self):
        service = AnalyticsService()
        trend = _build_skill_trend_from_values("grammar", [])
        assert trend.current_value is None
        assert trend.trend == "stable"
