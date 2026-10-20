"""API tests for POST /api/v1/plans/generate (mocked LLM)."""

import json

from fastapi.testclient import TestClient

from app.api.dependencies import get_llm_provider
from app.domain.interfaces import LLMProvider
from app.domain.models import LLMResult
from app.main import app

_VALID_PLAN = {
    "segments": [
        {
            "start": 0.0,
            "end": 2.0,
            "emotion": "neutral",
            "gaze": "camera",
        },
        {
            "start": 2.0,
            "end": 4.0,
            "emotion": "serious",
            "gesture": "emphasize",
            "headMotion": "nod",
            "gaze": "camera",
        },
    ]
}


class _FakePlanLLM(LLMProvider):
    """Returns fixed AnimationPlan JSON."""

    def generate(
        self,
        prompt: str,
        *,
        max_output_tokens: int | None = None,
    ) -> LLMResult:
        return LLMResult(text=json.dumps(_VALID_PLAN))


class _InvalidPlanLLM(LLMProvider):
    """Returns JSON with an illegal gesture name."""

    def generate(
        self,
        prompt: str,
        *,
        max_output_tokens: int | None = None,
    ) -> LLMResult:
        return LLMResult(
            text=json.dumps(
                {"segments": [{"start": 0, "end": 1, "gesture": "wave"}]}
            )
        )


client = TestClient(app)


def teardown_function() -> None:
    """Clear FastAPI overrides after each test."""
    app.dependency_overrides.clear()


def test_generate_plan_ok() -> None:
    """Route returns validated camelCase AnimationPlan JSON."""
    app.dependency_overrides[get_llm_provider] = lambda: _FakePlanLLM()
    response = client.post(
        "/api/v1/plans/generate",
        json={"topic": "market open"},
    )
    assert response.status_code == 200
    body = response.json()
    assert len(body["segments"]) == 2
    assert body["segments"][1]["headMotion"] == "nod"
    assert "head_motion" not in body["segments"][1]


def test_generate_plan_invalid_semantics_is_400() -> None:
    """Invalid LLM semantics surface as 400 PlanValidationError."""
    app.dependency_overrides[get_llm_provider] = lambda: _InvalidPlanLLM()
    response = client.post(
        "/api/v1/plans/generate",
        json={"topic": "market open"},
    )
    assert response.status_code == 400
    assert "gesture" in response.json()["detail"].lower()
