"""Animation plan routes. Thin layer — orchestration stays in services."""

from fastapi import APIRouter, Depends, HTTPException

from app.api.dependencies import (
    get_presenter_plan_service,
    get_presenter_plan_service_with_llm,
)
from app.api.schemas import (
    AnimationPlanSchema,
    AnimationSegmentSchema,
    GeneratePlanRequest,
    GeneratePlanTextRequest,
    GeneratePlanTextResponse,
)
from app.core.exceptions import (
    LlmConfigurationError,
    LlmProviderError,
    PlanValidationError,
)
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


@router.post("/generate-text", response_model=GeneratePlanTextResponse)
def generate_plan_text(
    body: GeneratePlanTextRequest,
    service: PresenterPlanService = Depends(get_presenter_plan_service_with_llm),
) -> GeneratePlanTextResponse:
    """Generate a short spoken script for a topic via the LLM port."""
    try:
        text = service.generate_plan_text(body.topic)
    except PlanValidationError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except LlmConfigurationError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except LlmProviderError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    return GeneratePlanTextResponse(text=text)


@router.post("/generate", response_model=AnimationPlanSchema)
def generate_plan(
    body: GeneratePlanRequest,
    service: PresenterPlanService = Depends(get_presenter_plan_service_with_llm),
) -> AnimationPlanSchema:
    """
    Generate a validated semantic ``AnimationPlan`` from a topic via the LLM.

    Response shape matches ``GET /plans/sample`` (camelCase ``headMotion``).
    """
    try:
        plan = service.generate_plan(body.topic)
    except PlanValidationError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except LlmConfigurationError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except LlmProviderError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    return _to_schema(plan)
