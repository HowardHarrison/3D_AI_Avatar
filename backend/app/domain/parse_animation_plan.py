"""Parse and validate semantic AnimationPlan payloads (LLM / API JSON)."""

from __future__ import annotations

import json
import re
from typing import Any, get_args

from app.core.exceptions import PlanValidationError
from app.domain.models import (
    AnimationPlan,
    AnimationSegment,
    ExpressionName,
    GazeTarget,
    GestureName,
    HeadMotionName,
)

_EMOTIONS = frozenset(get_args(ExpressionName))
_GESTURES = frozenset(get_args(GestureName))
_HEAD_MOTIONS = frozenset(get_args(HeadMotionName))
_GAZES = frozenset(get_args(GazeTarget))
_FENCE_RE = re.compile(
    r"^```(?:json)?\s*(.*?)\s*```$",
    re.DOTALL | re.IGNORECASE,
)


def parse_animation_plan(raw: str | dict[str, Any] | list[Any]) -> AnimationPlan:
    """
    Validate a raw plan (JSON string or object) into a domain ``AnimationPlan``.

    Accepts camelCase ``headMotion`` (frontend / LLM contract). Rejects unknown
    semantic names so invalid LLM output never reaches clients unchecked.

    Args:
        raw: JSON text from an LLM, or an already-decoded object.

    Returns:
        Validated ``AnimationPlan``.

    Raises:
        PlanValidationError: On JSON or semantic validation failure.
    """
    data = _coerce_object(raw)
    if not isinstance(data, dict) or "segments" not in data:
        raise PlanValidationError("Animation plan must include a segments array.")
    segments_raw = data["segments"]
    if not isinstance(segments_raw, list):
        raise PlanValidationError("Animation plan segments must be an array.")
    if len(segments_raw) == 0:
        raise PlanValidationError("Animation plan must include at least one segment.")

    segments = tuple(
        _parse_segment(segment, index) for index, segment in enumerate(segments_raw)
    )
    return AnimationPlan(segments=segments)


def _coerce_object(raw: str | dict[str, Any] | list[Any]) -> Any:
    """Decode JSON text (optionally fenced) into a Python object."""
    if isinstance(raw, (dict, list)):
        return raw
    text = raw.strip()
    if not text:
        raise PlanValidationError("Animation plan JSON is empty.")
    fenced = _FENCE_RE.match(text)
    if fenced:
        text = fenced.group(1).strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        start = text.find("{")
        end = text.rfind("}")
        if start >= 0 and end > start:
            try:
                return json.loads(text[start : end + 1])
            except json.JSONDecodeError as exc:
                raise PlanValidationError(
                    f"Animation plan JSON is invalid: {exc.msg}"
                ) from exc
        raise PlanValidationError("Animation plan JSON is invalid.") from None


def _parse_segment(segment: Any, index: int) -> AnimationSegment:
    """Validate one segment object into an ``AnimationSegment``."""
    if not isinstance(segment, dict):
        raise PlanValidationError(f"Segment {index} must be an object.")

    start = segment.get("start")
    end = segment.get("end")
    if not isinstance(start, (int, float)) or not isinstance(end, (int, float)):
        raise PlanValidationError(
            f"Segment {index} must include numeric start and end."
        )
    start_f = float(start)
    end_f = float(end)
    if end_f < start_f:
        raise PlanValidationError(f"Segment {index} end must be >= start.")

    emotion = _optional_enum(segment, "emotion", _EMOTIONS, index)
    gesture = _optional_enum(segment, "gesture", _GESTURES, index)
    head_motion = _optional_enum(
        segment,
        "headMotion",
        _HEAD_MOTIONS,
        index,
        alt_key="head_motion",
    )
    gaze = _optional_enum(segment, "gaze", _GAZES, index)

    return AnimationSegment(
        start=start_f,
        end=end_f,
        emotion=emotion,  # type: ignore[arg-type]
        gesture=gesture,  # type: ignore[arg-type]
        head_motion=head_motion,  # type: ignore[arg-type]
        gaze=gaze,  # type: ignore[arg-type]
    )


def _optional_enum(
    segment: dict[str, Any],
    key: str,
    allowed: frozenset[str],
    index: int,
    *,
    alt_key: str | None = None,
) -> str | None:
    """Read an optional semantic name; reject unknown values."""
    value = segment.get(key)
    if value is None and alt_key is not None:
        value = segment.get(alt_key)
    if value is None:
        return None
    if not isinstance(value, str) or value not in allowed:
        raise PlanValidationError(f"Segment {index} has an invalid {key}.")
    return value
