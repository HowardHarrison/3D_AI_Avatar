"""Health check route."""

from fastapi import APIRouter

from app.api.schemas import HealthResponse

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
def health_check() -> HealthResponse:
    """Return API liveness status."""
    return HealthResponse(status="ok")
