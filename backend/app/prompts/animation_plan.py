"""Prompt templates for LLM-produced semantic AnimationPlan JSON."""

from typing import get_args

from app.domain.models import (
    ExpressionName,
    GazeTarget,
    GestureName,
    HeadMotionName,
)


def build_animation_plan_prompt(topic: str) -> str:
    """
    Ask the model for a JSON AnimationPlan matching the frontend contract.

    Args:
        topic: News or segment topic (already trimmed by the caller).

    Returns:
        Prompt string for ``LLMProvider.generate``.
    """
    emotions = ", ".join(get_args(ExpressionName))
    gestures = ", ".join(get_args(GestureName))
    head_motions = ", ".join(get_args(HeadMotionName))
    gazes = ", ".join(get_args(GazeTarget))
    return (
        "You plan timed performance for a 3D news-presenter avatar.\n"
        f"Topic: {topic}\n"
        "Return ONLY valid JSON (no markdown fences, no commentary) with this shape:\n"
        '{"segments":[{"start":0.0,"end":2.0,"emotion":"neutral",'
        '"gesture":"emphasize","headMotion":"nod","gaze":"camera"}]}\n'
        "Rules:\n"
        "- Include 2 to 5 segments.\n"
        "- start/end are seconds; each end must be >= start; times should progress.\n"
        f"- emotion must be one of: {emotions} (or omit).\n"
        f"- gesture must be one of: {gestures} (or omit).\n"
        f"- headMotion must be one of: {head_motions} (or omit).\n"
        f"- gaze must be one of: {gazes} (or omit).\n"
        "- Use camelCase key headMotion (not head_motion).\n"
        "- Do not invent other field names or action names."
    )
