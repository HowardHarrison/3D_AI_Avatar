"""API tests for POST /api/v1/chat/turns (mocked LLM)."""

from fastapi.testclient import TestClient

from app.api.dependencies import get_llm_provider
from app.domain.interfaces import LLMProvider
from app.domain.models import LLMResult
from app.main import app


class _FakeLLM(LLMProvider):
    """In-memory LLM port that echoes whether history was in the prompt."""

    last_prompt: str = ""

    def generate(
        self,
        prompt: str,
        *,
        max_output_tokens: int | None = None,
    ) -> LLMResult:
        _FakeLLM.last_prompt = prompt
        return LLMResult(text="Hello! I am glad you asked.")


client = TestClient(app)


def setup_function() -> None:
    """Install fake LLM before each test."""
    _FakeLLM.last_prompt = ""
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


def test_chat_turn_with_history() -> None:
    """History is included in the LLM prompt."""
    response = client.post(
        "/api/v1/chat/turns",
        json={
            "message": "What is my name?",
            "history": [
                {"role": "user", "content": "My name is Sam."},
                {"role": "assistant", "content": "Nice to meet you, Sam!"},
            ],
        },
    )
    assert response.status_code == 200
    assert "My name is Sam." in _FakeLLM.last_prompt
    assert "Nice to meet you, Sam!" in _FakeLLM.last_prompt
    assert "What is my name?" in _FakeLLM.last_prompt


def test_chat_turn_rejects_empty_message() -> None:
    """Pydantic rejects blank message before the service runs."""
    response = client.post(
        "/api/v1/chat/turns",
        json={"message": ""},
    )
    assert response.status_code == 422
