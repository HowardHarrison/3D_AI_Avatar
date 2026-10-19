"""LLM provider port. Implementations live under infrastructure/ (e.g. LangChain later)."""

from abc import ABC, abstractmethod

from app.domain.models import LLMResult


class LLMProvider(ABC):
    """Interface for large language model text generation."""

    @abstractmethod
    def generate(
        self,
        prompt: str,
        *,
        max_output_tokens: int | None = None,
    ) -> LLMResult:
        """Generate a text response from the given prompt."""
