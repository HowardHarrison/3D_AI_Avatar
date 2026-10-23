"""FastAPI dependency injection wiring."""

from functools import lru_cache

from fastapi import Depends

from app.core.exceptions import LlmConfigurationError
from app.core.settings import get_settings
from app.domain.interfaces import LLMProvider
from app.infrastructure.openai_compatible import OpenAICompatibleLLMProvider
from app.services.chat_service import ChatService
from app.services.presenter_plan_service import PresenterPlanService


@lru_cache
def get_presenter_plan_service() -> PresenterPlanService:
    """Provide a shared PresenterPlanService without an LLM (sample plan)."""
    return PresenterPlanService()


@lru_cache
def get_llm_provider() -> LLMProvider:
    """
    Build the configured OpenAI-compatible ``LLMProvider``.

    Reads ``LLM_API_KEY``, ``LLM_MODEL``, and optional ``LLM_BASE_URL`` from settings.

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


def get_presenter_plan_service_with_llm(
    llm: LLMProvider = Depends(get_llm_provider),
) -> PresenterPlanService:
    """
    PresenterPlanService with an injected LLM port (for generate-text routes).

    Not cached: FastAPI builds a thin service wrapper per request; the LLM
    client itself stays cached via ``get_llm_provider``.
    """
    return PresenterPlanService(llm=llm)


def get_chat_service(
    llm: LLMProvider = Depends(get_llm_provider),
) -> ChatService:
    """
    ChatService with an injected LLM port (for chat turn routes).

    Not cached: thin per-request wrapper; LLM client stays cached.
    """
    return ChatService(llm=llm)
