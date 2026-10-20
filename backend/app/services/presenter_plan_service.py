"""Presenter plan use cases. Sample plan is deterministic; LLM builds text/plans."""

import logging

from app.core.exceptions import LlmConfigurationError, PlanValidationError
from app.domain.interfaces import LLMProvider
from app.domain.models import AnimationPlan, AnimationSegment
from app.domain.parse_animation_plan import parse_animation_plan
from app.prompts import build_animation_plan_prompt, build_plan_script_prompt

logger = logging.getLogger(__name__)


class PresenterPlanService:
    """Orchestrates animation plans and plan-related text for avatar clients."""

    def __init__(self, llm: LLMProvider | None = None) -> None:
        """
        Create the service.

        Args:
            llm: Optional LLM port. Required for LLM-backed methods;
                sample plans work without it.
        """
        self._llm = llm

    def _require_llm(self) -> LLMProvider:
        """Return the injected LLM port or raise if missing."""
        if self._llm is None:
            raise LlmConfigurationError(
                "LLM provider is not configured for this service instance"
            )
        return self._llm

    def _require_topic(self, topic: str) -> str:
        """Trim and validate a topic string."""
        cleaned = topic.strip()
        if not cleaned:
            raise PlanValidationError("topic must not be empty")
        return cleaned

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

    def generate_plan_text(self, topic: str) -> str:
        """
        Generate a short spoken script for a future animation plan.

        Args:
            topic: Subject of the news/presenter segment.

        Returns:
            Plain-text script from the configured ``LLMProvider``.

        Raises:
            PlanValidationError: If ``topic`` is blank.
            LlmConfigurationError: If no LLM was injected.
            LlmProviderError: Propagated from the provider on API failure.
        """
        cleaned = self._require_topic(topic)
        llm = self._require_llm()
        prompt = build_plan_script_prompt(cleaned)
        logger.info("Generating plan script text via LLM port")
        return llm.generate(prompt, max_output_tokens=300).text

    def generate_plan(self, topic: str) -> AnimationPlan:
        """
        Ask the LLM for semantic AnimationPlan JSON and validate it.

        Args:
            topic: Subject of the news/presenter segment.

        Returns:
            Domain ``AnimationPlan`` safe for API serialization.

        Raises:
            PlanValidationError: Blank topic or invalid LLM JSON / semantics.
            LlmConfigurationError: If no LLM was injected.
            LlmProviderError: Propagated from the provider on API failure.
        """
        cleaned = self._require_topic(topic)
        llm = self._require_llm()
        prompt = build_animation_plan_prompt(cleaned)
        logger.info("Generating AnimationPlan JSON via LLM port")
        raw = llm.generate(prompt, max_output_tokens=800).text
        return parse_animation_plan(raw)
