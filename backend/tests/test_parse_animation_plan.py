"""Unit tests for AnimationPlan JSON parsing / validation."""

import pytest

from app.core.exceptions import PlanValidationError
from app.domain.parse_animation_plan import parse_animation_plan


def test_parse_valid_plan_with_head_motion() -> None:
    """camelCase headMotion maps to domain head_motion."""
    plan = parse_animation_plan(
        {
            "segments": [
                {
                    "start": 0,
                    "end": 2,
                    "emotion": "serious",
                    "gesture": "emphasize",
                    "headMotion": "nod",
                    "gaze": "camera",
                }
            ]
        }
    )
    assert len(plan.segments) == 1
    assert plan.segments[0].head_motion == "nod"
    assert plan.segments[0].gesture == "emphasize"


def test_parse_strips_markdown_fence() -> None:
    """LLM fenced JSON is accepted."""
    raw = """```json
{"segments":[{"start":0,"end":1,"gaze":"camera"}]}
```"""
    plan = parse_animation_plan(raw)
    assert plan.segments[0].gaze == "camera"


def test_reject_unknown_gesture() -> None:
    """Unknown semantic names fail validation."""
    with pytest.raises(PlanValidationError, match="invalid gesture"):
        parse_animation_plan(
            {"segments": [{"start": 0, "end": 1, "gesture": "wave"}]}
        )


def test_reject_end_before_start() -> None:
    """end must be >= start."""
    with pytest.raises(PlanValidationError, match="end must be"):
        parse_animation_plan({"segments": [{"start": 2, "end": 1}]})
