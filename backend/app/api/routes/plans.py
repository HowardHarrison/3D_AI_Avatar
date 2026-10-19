"""Animation plan routes. Thin layer — orchestration stays in services."""

from fastapi import APIRouter, Depends

from app.api.dependencies import get_presenter_plan_service
from app.api.schemas import AnimationPlanSchema, AnimationSegmentSchema
from app.domain.models import AnimationPlan
from app.services.presenter_plan_service import PresenterPlanService

router = APIRouter(prefix="/plans", tags=["plans"])


def _to_schema(plan: AnimationPlan) -> AnimationPlanSchema:
    """Map domain plan to API schema with camelCase aliases."""
    return AnimationPlanSchema(
        segments=[
            AnimationSegmentSchema(
                start=segment.start,
                end=segment.end,
                emotion=segment.emotion,
                gesture=segment.gesture,
                headMotion=segment.head_motion,
                gaze=segment.gaze,
            )
            for segment in plan.segments
        ]
    )


@router.get("/sample", response_model=AnimationPlanSchema)
def get_sample_plan(
    service: PresenterPlanService = Depends(get_presenter_plan_service),
) -> AnimationPlanSchema:
    """Return a hardcoded sample plan for frontend/mobile integration tests."""
    return _to_schema(service.get_sample_plan())
