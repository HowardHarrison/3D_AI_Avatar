"""TTS provider port. Implementations live under infrastructure/."""

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class TtsResult:
    """Synthesized speech metadata and optional audio URL or bytes path."""

    audio_url: str
    duration_seconds: float


class TtsProvider(ABC):
    """Interface for text-to-speech synthesis."""

    @abstractmethod
    def synthesize(self, text: str, *, voice_id: str | None = None) -> TtsResult:
        """Synthesize speech and return a playable URL plus duration."""
