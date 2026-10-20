"""OpenAI-compatible HTTP adapters (official OpenAI API and compatible gateways)."""

from app.infrastructure.openai_compatible.llm_provider import (
    OpenAICompatibleLLMProvider,
)

__all__ = ["OpenAICompatibleLLMProvider"]
