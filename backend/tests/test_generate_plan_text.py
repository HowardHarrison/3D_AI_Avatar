"""API tests for POST /api/v1/plans/generate-text (mocked LLM)."""

from fastapi.testclient import TestClient

from app.api.dependencies import get_llm_provider
from app.domain.interfaces import LLMProvider
from app.domain.models import LLMResult
from app.main import app


class _FakeLLM(LLMProvider):
    """In-memory LLM port for route tests."""

    def generate(
        self,
        prompt: str,
        *,
        max_output_tokens: int | None = None,
    ) -> LLMResult:
        return LLMResult(text=f"SCRIPT:{prompt[:24]}")


client = TestClient(app)


def setup_function() -> None:
    """Install fake LLM before each test."""
    app.dependency_overrides[get_llm_provider] = lambda: _FakeLLM()


def teardown_function() -> None:
    """Clear FastAPI overrides after each test."""
    app.dependency_overrides.clear()


def test_generate_plan_text_ok() -> None:
    """Route injects LLM via DI and returns generated text."""
    response = client.post(
        "/api/v1/plans/generate-text",
        json={"topic": "local weather update"},
    )
    assert response.status_code == 200
    body = response.json()
    assert "text" in body
    assert body["text"].startswith("SCRIPT:")


def test_generate_plan_text_rejects_empty_topic() -> None:
    """Pydantic rejects blank topic before the service runs."""
    response = client.post(
        "/api/v1/plans/generate-text",
        json={"topic": ""},
    )
    assert response.status_code == 422
