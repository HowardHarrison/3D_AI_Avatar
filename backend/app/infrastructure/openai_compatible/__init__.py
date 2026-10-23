"""OpenAI-compatible HTTP adapters (official OpenAI API and compatible gateways)."""

from app.infrastructure.openai_compatible.llm_provider import (
    OpenAICompatibleLLMProvider,
)
from app.infrastructure.openai_compatible.tts_provider import (
    OpenAICompatibleTtsProvider,
)

__all__ = ["OpenAICompatibleLLMProvider", "OpenAICompatibleTtsProvider"]
