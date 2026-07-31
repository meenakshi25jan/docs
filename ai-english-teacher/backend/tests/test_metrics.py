"""Prometheus /metrics endpoint tests."""

from fastapi.testclient import TestClient

from app.main import app


def test_metrics_endpoint_returns_prometheus_text() -> None:
    client = TestClient(app)
    if not app.state.prometheus_metrics_mounted:
        return  # skip when prometheus-client not installed in CI slim env
    response = client.get("/metrics")
    assert response.status_code == 200
    assert "text/plain" in response.headers.get("content-type", "")
    body = response.text
    assert "# HELP" in body or "# TYPE" in body
