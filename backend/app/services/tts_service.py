"""TTS use cases: text → playable audio URL via the TTS port."""

import logging
import re
from pathlib import Path

from app.core.exceptions import TtsConfigurationError, TtsValidationError
from app.domain.interfaces.tts_provider import TtsProvider, TtsResult

logger = logging.getLogger(__name__)

_AUDIO_FILE = re.compile(r"^[a-f0-9]{32}\.mp3$")


class TtsService:
    """Orchestrates speech synthesis for avatar clients."""

    def __init__(self, tts: TtsProvider | None = None, *, cache_dir: Path) -> None:
        """
        Create the service.

        Args:
            tts: TTS port. Required for ``synthesize``; optional for audio file lookup.
            cache_dir: Directory where synthesized MP3 files are stored.
        """
        self._tts = tts
        self._cache_dir = cache_dir
        self._cache_dir.mkdir(parents=True, exist_ok=True)

    def synthesize(self, text: str, *, voice_id: str | None = None) -> TtsResult:
        """
        Synthesize speech for the given text.

        Args:
            text: Words to speak.
            voice_id: Optional voice override.

        Returns:
            ``TtsResult`` with relative audio URL and estimated duration.

        Raises:
            TtsValidationError: If ``text`` is blank.
            TtsConfigurationError: If the TTS port is missing.
            TtsProviderError: Propagated from the provider.
        """
        cleaned = text.strip()
        if not cleaned:
            raise TtsValidationError("text must not be empty")
        if self._tts is None:
            raise TtsConfigurationError("TTS provider is not configured")
        logger.info("Synthesizing speech via TTS port (%s chars)", len(cleaned))
        return self._tts.synthesize(cleaned, voice_id=voice_id)

    def resolve_audio_path(self, file_id: str) -> Path:
        """
        Resolve a safe path for a cached MP3 id.

        Args:
            file_id: Filename like ``{uuid32}.mp3``.

        Returns:
            Absolute path under the cache directory.

        Raises:
            TtsValidationError: If the id is unsafe or the file is missing.
        """
        if not _AUDIO_FILE.match(file_id):
            raise TtsValidationError("invalid audio file id")
        path = (self._cache_dir / file_id).resolve()
        if not str(path).startswith(str(self._cache_dir.resolve())):
            raise TtsValidationError("invalid audio file id")
        if not path.is_file():
            raise TtsValidationError("audio file not found")
        return path
