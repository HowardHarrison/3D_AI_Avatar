"""FastAPI dependency injection wiring."""

from functools import lru_cache

from app.core.exceptions import LlmConfigurationError
from app.core.settings import get_settings
from app.domain.interfaces import LLMProvider
from app.infrastructure.openai_compatible import OpenAICompatibleLLMProvider
from app.services.presenter_plan_service import PresenterPlanService


@lru_cache
def get_presenter_plan_service() -> PresenterPlanService:
    """Provide a shared PresenterPlanService instance."""
    return PresenterPlanService()


@lru_cache
def get_llm_provider() -> LLMProvider:
    """
    Build the configured OpenAI-compatible ``LLMProvider``.

    Reads ``LLM_API_KEY``, ``LLM_MODEL``, and optional ``LLM_BASE_URL`` from settings.
    Not used by routes yet — available for the next service/route step.

    Raises:
        LlmConfigurationError: If the API key is missing or blank.
    """
    settings = get_settings()
    api_key = (settings.llm_api_key or "").strip()
    if not api_key:
        raise LlmConfigurationError(
            "LLM_API_KEY is not set. Add it to backend/.env (see .env.example)."
        )
    base_url = (settings.llm_base_url or "").strip() or None
    return OpenAICompatibleLLMProvider(
        api_key=api_key,
        model=settings.llm_model,
        base_url=base_url,
    )
