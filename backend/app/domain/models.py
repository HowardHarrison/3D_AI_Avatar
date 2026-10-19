"""Core domain models for presenter plans (semantic only — no bones/clips)."""

from dataclasses import dataclass, field
from typing import Literal

GestureName = Literal[
    "openHand",
    "emphasize",
    "pointLeft",
    "pointRight",
    "handsTogether",
]
ExpressionName = Literal["neutral", "serious", "positive", "concerned"]
HeadMotionName = Literal["nod", "turnLeft", "turnRight", "tiltLeft", "tiltRight"]
GazeTarget = Literal["camera", "left", "right", "down"]


@dataclass(frozen=True, slots=True)
class AnimationSegment:
    """One timed slice of a presenter performance plan."""

    start: float
    end: float
    emotion: ExpressionName | None = None
    gesture: GestureName | None = None
    head_motion: HeadMotionName | None = None
    gaze: GazeTarget | None = None


@dataclass(frozen=True, slots=True)
class AnimationPlan:
    """Sequence of semantic animation segments for web/mobile clients."""

    segments: tuple[AnimationSegment, ...] = field(default_factory=tuple)


@dataclass(frozen=True, slots=True)
class LLMResult:
    """Raw text result from an LLM provider."""

    text: str
