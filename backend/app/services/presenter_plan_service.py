"""Presenter plan use cases. No LLM calls yet — returns a deterministic sample."""

import logging

from app.domain.models import AnimationPlan, AnimationSegment

logger = logging.getLogger(__name__)


class PresenterPlanService:
    """Orchestrates animation plans for the avatar clients."""

    def get_sample_plan(self) -> AnimationPlan:
        """
        Return a fixed semantic plan for local integration testing.

        Matches frontend `AnimationPlan` / `parseAnimationPlan` field names
        when serialized via API schemas (camelCase for headMotion).
        """
        logger.info("Building sample presenter plan")
        return AnimationPlan(
            segments=(
                AnimationSegment(
                    start=0.0,
                    end=2.0,
                    emotion="neutral",
                    gaze="camera",
                ),
                AnimationSegment(
                    start=2.0,
                    end=4.5,
                    emotion="serious",
                    gesture="emphasize",
                    head_motion="nod",
                    gaze="camera",
                ),
                AnimationSegment(
                    start=4.5,
                    end=6.0,
                    emotion="positive",
                    gesture="openHand",
                    gaze="camera",
                ),
            )
        )
