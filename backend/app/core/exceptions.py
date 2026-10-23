"""Domain and application exceptions."""


class AppError(Exception):
    """Base application error."""


class PlanValidationError(AppError):
    """Raised when an animation plan fails semantic validation."""


class ChatValidationError(AppError):
    """Raised when a chat turn request fails validation."""


class LlmConfigurationError(AppError):
    """Raised when LLM settings are missing or invalid for a provider call."""


class LlmProviderError(AppError):
    """Raised when an LLM provider request fails."""


class TtsValidationError(AppError):
    """Raised when a TTS request fails validation."""


class TtsConfigurationError(AppError):
    """Raised when TTS settings are missing or invalid for a provider call."""


class TtsProviderError(AppError):
    """Raised when a TTS provider request fails."""
