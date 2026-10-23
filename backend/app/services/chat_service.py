"""Chat turn use cases. One user message → one assistant reply via LLM port."""

import logging

from app.core.exceptions import ChatValidationError, LlmConfigurationError
from app.domain.interfaces import LLMProvider
from app.prompts import build_chat_turn_prompt

logger = logging.getLogger(__name__)


class ChatService:
    """Orchestrates interactive chatbot turns for avatar clients."""

    def __init__(self, llm: LLMProvider) -> None:
        """
        Create the service.

        Args:
            llm: Required LLM port used to generate the assistant reply.
        """
        self._llm = llm

    def send_turn(self, message: str) -> str:
        """
        Generate one assistant reply for a user message.

        Args:
            message: User text from the chat UI.

        Returns:
            Plain-text assistant reply.

        Raises:
            ChatValidationError: If ``message`` is blank.
            LlmConfigurationError: If the LLM port is somehow missing.
            LlmProviderError: Propagated from the provider on API failure.
        """
        cleaned = message.strip()
        if not cleaned:
            raise ChatValidationError("message must not be empty")
        if self._llm is None:
            raise LlmConfigurationError("LLM provider is not configured for chat")
        prompt = build_chat_turn_prompt(cleaned)
        logger.info("Generating chat turn reply via LLM port")
        return self._llm.generate(prompt, max_output_tokens=250).text.strip()
