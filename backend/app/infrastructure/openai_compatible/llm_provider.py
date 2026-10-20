"""OpenAI-compatible ``LLMProvider`` adapter (reads API key / model / base URL)."""

from openai import APIError, OpenAI

from app.core.exceptions import LlmConfigurationError, LlmProviderError
from app.domain.interfaces import LLMProvider
from app.domain.models import LLMResult


class OpenAICompatibleLLMProvider(LLMProvider):
    """Chat Completions client for OpenAI and OpenAI-compatible base URLs."""

    def __init__(
        self,
        *,
        api_key: str,
        model: str,
        base_url: str | None = None,
    ) -> None:
        """
        Create a provider bound to one model endpoint.

        Args:
            api_key: Provider secret (never log this value).
            model: Model id (e.g. ``gpt-4o-mini``).
            base_url: Optional OpenAI-compatible API root; ``None`` uses OpenAI default.

        Raises:
            LlmConfigurationError: If ``api_key`` or ``model`` is empty.
        """
        key = api_key.strip()
        model_id = model.strip()
        if not key:
            raise LlmConfigurationError("LLM_API_KEY is empty")
        if not model_id:
            raise LlmConfigurationError("LLM_MODEL is empty")

        client_kwargs: dict[str, str] = {"api_key": key}
        if base_url and base_url.strip():
            client_kwargs["base_url"] = base_url.strip()

        self._client = OpenAI(**client_kwargs)
        self._model = model_id

    def generate(
        self,
        prompt: str,
        *,
        max_output_tokens: int | None = None,
    ) -> LLMResult:
        """
        Generate text from a single user prompt via Chat Completions.

        Args:
            prompt: User message content.
            max_output_tokens: Optional completion token cap.

        Returns:
            ``LLMResult`` with the assistant text (empty string if none).

        Raises:
            LlmProviderError: On API or transport failures.
        """
        create_kwargs: dict[str, object] = {
            "model": self._model,
            "messages": [{"role": "user", "content": prompt}],
        }
        if max_output_tokens is not None:
            create_kwargs["max_tokens"] = max_output_tokens

        try:
            response = self._client.chat.completions.create(**create_kwargs)
        except APIError as exc:
            raise LlmProviderError(f"LLM request failed: {exc}") from exc
        except Exception as exc:  # noqa: BLE001 — map SDK/network errors to domain
            raise LlmProviderError(f"LLM request failed: {exc}") from exc

        choice = response.choices[0] if response.choices else None
        text = (choice.message.content if choice and choice.message else None) or ""
        return LLMResult(text=text)
