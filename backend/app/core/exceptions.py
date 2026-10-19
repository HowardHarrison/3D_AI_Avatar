"""Domain and application exceptions."""


class AppError(Exception):
    """Base application error."""


class PlanValidationError(AppError):
    """Raised when an animation plan fails semantic validation."""
