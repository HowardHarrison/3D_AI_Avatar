"""TTS routes. Thin layer — orchestration stays in services."""

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse

from app.api.dependencies import get_tts_audio_service, get_tts_service
from app.api.schemas import SynthesizeSpeechRequest, SynthesizeSpeechResponse
from app.core.exceptions import (
    TtsConfigurationError,
    TtsProviderError,
    TtsValidationError,
)
from app.services.tts_service import TtsService

router = APIRouter(prefix="/tts", tags=["tts"])


@router.post("/synthesize", response_model=SynthesizeSpeechResponse)
def synthesize_speech(
    body: SynthesizeSpeechRequest,
    service: TtsService = Depends(get_tts_service),
) -> SynthesizeSpeechResponse:
    """
    Synthesize speech for ``text`` and return a playable audio URL.

    Audio bytes are cached server-side; clients fetch ``audioUrl`` next.
    """
    try:
        result = service.synthesize(body.text, voice_id=body.voice_id)
    except TtsValidationError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except TtsConfigurationError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except TtsProviderError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    return SynthesizeSpeechResponse(
        audio_url=result.audio_url,
        duration_seconds=result.duration_seconds,
    )


@router.get("/audio/{file_id}")
def get_synthesized_audio(
    file_id: str,
    service: TtsService = Depends(get_tts_audio_service),
) -> FileResponse:
    """Serve a previously synthesized MP3 from the local TTS cache."""
    try:
        path = service.resolve_audio_path(file_id)
    except TtsValidationError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return FileResponse(path, media_type="audio/mpeg", filename=file_id)
