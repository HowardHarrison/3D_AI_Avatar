"""FastAPI dependency injection wiring."""

from functools import lru_cache

from app.services.presenter_plan_service import PresenterPlanService


@lru_cache
def get_presenter_plan_service() -> PresenterPlanService:
    """Provide a shared PresenterPlanService instance."""
    return PresenterPlanService()
