"""Smoke tests for the health endpoint."""

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_ok() -> None:
    """Health endpoint returns ok."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_sample_plan_has_segments() -> None:
    """Sample plan returns semantic segments with camelCase headMotion."""
    response = client.get("/api/v1/plans/sample")
    assert response.status_code == 200
    body = response.json()
    assert "segments" in body
    assert len(body["segments"]) >= 1
    second = body["segments"][1]
    assert second.get("headMotion") == "nod"
    assert "head_motion" not in second
