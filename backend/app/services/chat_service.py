"""Chat turn use cases. User message (+ optional history) → assistant reply."""

from __future__ import annotations

import logging
from typing import Literal, Sequence

from app.core.exceptions import ChatValidationError, LlmConfigurationError
from app.domain.interfaces import LLMProvider
from app.prompts import build_chat_turn_prompt

logger = logging.getLogger(__name__)

ChatRole = Literal["user", "assistant"]

# Keep prompts bounded for learning / cost control.
_MAX_HISTORY_MESSAGES = 12
_MAX_HISTORY_CHARS = 500


class ChatService:
    """Orchestrates interactive chatbot turns for avatar clients."""

    def __init__(self, llm: LLMProvider) -> None:
        """
        Create the service.

        Args:
            llm: Required LLM port used to generate the assistant reply.
        """
        self._llm = llm

    def send_turn(
        self,
        message: str,
        *,
        history: Sequence[tuple[ChatRole, str]] | None = None,
    ) -> str:
        """
        Generate one assistant reply for a user message.

        Args:
            message: Latest user text from the chat UI.
            history: Prior turns as ``(role, text)`` pairs (chronological).

        Returns:
            Plain-text assistant reply.

        Raises:
            ChatValidationError: If ``message`` is blank or history is invalid.
            LlmConfigurationError: If the LLM port is somehow missing.
            LlmProviderError: Propagated from the provider on API failure.
        """
        cleaned = message.strip()
        if not cleaned:
            raise ChatValidationError("message must not be empty")
        if self._llm is None:
            raise LlmConfigurationError("LLM provider is not configured for chat")

        normalized = self._normalize_history(history)
        prompt = build_chat_turn_prompt(cleaned, normalized)
        logger.info(
            "Generating chat turn reply via LLM port (history=%s)",
            len(normalized),
        )
        return self._llm.generate(prompt, max_output_tokens=250).text.strip()

    def _normalize_history(
        self,
        history: Sequence[tuple[ChatRole, str]] | None,
    ) -> list[tuple[ChatRole, str]]:
        """Trim, validate, and cap prior messages."""
        if not history:
            return []

        cleaned: list[tuple[ChatRole, str]] = []
        for role, text in history:
            if role not in ("user", "assistant"):
                raise ChatValidationError("history role must be user or assistant")
            content = text.strip()
            if not content:
                continue
            if len(content) > _MAX_HISTORY_CHARS:
                content = content[:_MAX_HISTORY_CHARS].rstrip() + "…"
            cleaned.append((role, content))

        if len(cleaned) > _MAX_HISTORY_MESSAGES:
            cleaned = cleaned[-_MAX_HISTORY_MESSAGES:]
        return cleaned
