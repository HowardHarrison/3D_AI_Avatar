"""Unit tests for OpenAI-compatible LLMProvider (no live network)."""

from unittest.mock import MagicMock, patch

import pytest

from app.core.exceptions import LlmConfigurationError, LlmProviderError
from app.infrastructure.openai_compatible import OpenAICompatibleLLMProvider


def test_generate_returns_assistant_text() -> None:
    """generate() maps Chat Completions content into LLMResult.text."""
    mock_client = MagicMock()
    mock_client.chat.completions.create.return_value = MagicMock(
        choices=[MagicMock(message=MagicMock(content="hello from model"))]
    )

    with patch(
        "app.infrastructure.openai_compatible.llm_provider.OpenAI",
        return_value=mock_client,
    ):
        provider = OpenAICompatibleLLMProvider(
            api_key="test-key",
            model="gpt-4o-mini",
        )
        result = provider.generate("ping", max_output_tokens=32)

    assert result.text == "hello from model"
    mock_client.chat.completions.create.assert_called_once_with(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": "ping"}],
        max_tokens=32,
    )


def test_empty_api_key_raises_configuration_error() -> None:
    """Blank API key fails before any HTTP call."""
    with pytest.raises(LlmConfigurationError, match="LLM_API_KEY"):
        OpenAICompatibleLLMProvider(api_key="   ", model="gpt-4o-mini")


def test_api_error_becomes_llm_provider_error() -> None:
    """SDK APIError is wrapped as LlmProviderError."""
    from openai import APIError

    mock_client = MagicMock()
    mock_client.chat.completions.create.side_effect = APIError(
        message="rate limited",
        request=MagicMock(),
        body=None,
    )

    with patch(
        "app.infrastructure.openai_compatible.llm_provider.OpenAI",
        return_value=mock_client,
    ):
        provider = OpenAICompatibleLLMProvider(api_key="test-key", model="gpt-4o-mini")
        with pytest.raises(LlmProviderError, match="LLM request failed"):
            provider.generate("ping")
