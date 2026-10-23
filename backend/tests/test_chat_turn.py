"""API tests for POST /api/v1/chat/turns (mocked LLM)."""

from fastapi.testclient import TestClient

from app.api.dependencies import get_llm_provider
from app.domain.interfaces import LLMProvider
from app.domain.models import LLMResult
from app.main import app


class _FakeLLM(LLMProvider):
    """In-memory LLM port for chat route tests."""

    def generate(
        self,
        prompt: str,
        *,
        max_output_tokens: int | None = None,
    ) -> LLMResult:
        return LLMResult(text="Hello! I am glad you asked.")


client = TestClient(app)


def setup_function() -> None:
    """Install fake LLM before each test."""
    app.dependency_overrides[get_llm_provider] = lambda: _FakeLLM()


def teardown_function() -> None:
    """Clear FastAPI overrides after each test."""
    app.dependency_overrides.clear()


def test_chat_turn_ok() -> None:
    """Route injects LLM via DI and returns assistant reply."""
    response = client.post(
        "/api/v1/chat/turns",
        json={"message": "Hi there"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["reply"] == "Hello! I am glad you asked."


def test_chat_turn_rejects_empty_message() -> None:
    """Pydantic rejects blank message before the service runs."""
    response = client.post(
        "/api/v1/chat/turns",
        json={"message": ""},
    )
    assert response.status_code == 422
