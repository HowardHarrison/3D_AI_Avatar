"""FastAPI dependency injection wiring."""

from functools import lru_cache
from pathlib import Path

from fastapi import Depends

from app.core.exceptions import LlmConfigurationError, TtsConfigurationError
from app.core.settings import get_settings
from app.domain.interfaces import LLMProvider, TtsProvider
from app.infrastructure.openai_compatible import (
    OpenAICompatibleLLMProvider,
    OpenAICompatibleTtsProvider,
)
from app.services.chat_service import ChatService
from app.services.presenter_plan_service import PresenterPlanService
from app.services.tts_service import TtsService

# backend/ package root (parent of ``app/``)
_BACKEND_ROOT = Path(__file__).resolve().parents[2]
_TTS_CACHE_DIR = _BACKEND_ROOT / ".tts_cache"


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


@lru_cache
def get_tts_cache_dir() -> Path:
    """Local directory for synthesized MP3 files (gitignored)."""
    _TTS_CACHE_DIR.mkdir(parents=True, exist_ok=True)
    return _TTS_CACHE_DIR


@lru_cache
def get_tts_provider() -> TtsProvider:
    """
    Build the configured OpenAI-compatible ``TtsProvider``.

    Uses ``TTS_API_KEY`` when set; otherwise falls back to ``LLM_API_KEY``.

    Raises:
        TtsConfigurationError: If no API key is available.
    """
    settings = get_settings()
    api_key = (settings.tts_api_key or settings.llm_api_key or "").strip()
    if not api_key:
        raise TtsConfigurationError(
            "TTS_API_KEY (or LLM_API_KEY) is not set. Add it to backend/.env."
        )
    base_url = (settings.tts_base_url or settings.llm_base_url or "").strip() or None
    return OpenAICompatibleTtsProvider(
        api_key=api_key,
        model=settings.tts_model,
        voice=settings.tts_voice,
        cache_dir=get_tts_cache_dir(),
        base_url=base_url,
    )


def get_tts_service(
    tts: TtsProvider = Depends(get_tts_provider),
    cache_dir: Path = Depends(get_tts_cache_dir),
) -> TtsService:
    """TtsService with injected TTS port (for synthesize)."""
    return TtsService(tts=tts, cache_dir=cache_dir)


def get_tts_audio_service(
    cache_dir: Path = Depends(get_tts_cache_dir),
) -> TtsService:
    """TtsService without a provider — serve cached audio files only."""
    return TtsService(tts=None, cache_dir=cache_dir)
