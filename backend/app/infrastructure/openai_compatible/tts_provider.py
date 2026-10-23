"""OpenAI-compatible ``TtsProvider`` adapter (speech synthesis → local cache file)."""

from __future__ import annotations

import re
import uuid
from pathlib import Path

from openai import APIError, OpenAI

from app.core.exceptions import TtsConfigurationError, TtsProviderError
from app.domain.interfaces.tts_provider import TtsProvider, TtsResult

_SAFE_VOICE = re.compile(r"^[a-zA-Z0-9_-]{1,64}$")


class OpenAICompatibleTtsProvider(TtsProvider):
    """Speech client for OpenAI and OpenAI-compatible base URLs."""

    def __init__(
        self,
        *,
        api_key: str,
        model: str,
        voice: str,
        cache_dir: Path,
        base_url: str | None = None,
    ) -> None:
        """
        Create a TTS provider that writes MP3 files under ``cache_dir``.

        Args:
            api_key: Provider secret (never log this value).
            model: Speech model id (e.g. ``tts-1``).
            voice: Voice id (e.g. ``alloy``).
            cache_dir: Directory for synthesized MP3 files.
            base_url: Optional OpenAI-compatible API root.

        Raises:
            TtsConfigurationError: If required settings are empty.
        """
        key = api_key.strip()
        model_id = model.strip()
        voice_id = voice.strip()
        if not key:
            raise TtsConfigurationError("TTS API key is empty")
        if not model_id:
            raise TtsConfigurationError("TTS_MODEL is empty")
        if not voice_id or not _SAFE_VOICE.match(voice_id):
            raise TtsConfigurationError("TTS_VOICE is missing or invalid")

        client_kwargs: dict[str, str] = {"api_key": key}
        if base_url and base_url.strip():
            client_kwargs["base_url"] = base_url.strip()

        self._client = OpenAI(**client_kwargs)
        self._model = model_id
        self._voice = voice_id
        self._cache_dir = cache_dir
        self._cache_dir.mkdir(parents=True, exist_ok=True)

    def synthesize(self, text: str, *, voice_id: str | None = None) -> TtsResult:
        """
        Synthesize ``text`` to an MP3 under the cache dir.

        Args:
            text: Spoken content (caller should trim / validate).
            voice_id: Optional per-call voice override.

        Returns:
            ``TtsResult`` with a relative ``audio_url`` path and estimated duration.

        Raises:
            TtsConfigurationError: If ``voice_id`` override is invalid.
            TtsProviderError: On API or I/O failures.
        """
        voice = (voice_id or self._voice).strip()
        if not voice or not _SAFE_VOICE.match(voice):
            raise TtsConfigurationError("voice_id is missing or invalid")

        file_id = f"{uuid.uuid4().hex}.mp3"
        output_path = self._cache_dir / file_id

        try:
            response = self._client.audio.speech.create(
                model=self._model,
                voice=voice,
                input=text,
            )
            response.write_to_file(output_path)
        except APIError as exc:
            raise TtsProviderError(f"TTS request failed: {exc}") from exc
        except Exception as exc:  # noqa: BLE001 — map SDK/network/IO to domain
            raise TtsProviderError(f"TTS request failed: {exc}") from exc

        # OpenAI does not return duration; rough estimate for talk-window sizing.
        word_count = max(1, len(text.split()))
        duration = max(1.0, word_count * 0.35)

        return TtsResult(
            audio_url=f"/api/v1/tts/audio/{file_id}",
            duration_seconds=duration,
        )
