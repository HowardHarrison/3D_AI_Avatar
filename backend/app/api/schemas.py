"""HTTP request/response models. Mirror frontend AnimationPlan JSON."""

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

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


class HealthResponse(BaseModel):
    """Liveness payload."""

    status: str


class AnimationSegmentSchema(BaseModel):
    """One timed semantic segment (camelCase for TS clients)."""

    model_config = ConfigDict(populate_by_name=True, ser_json_by_alias=True)

    start: float
    end: float
    emotion: ExpressionName | None = None
    gesture: GestureName | None = None
    head_motion: HeadMotionName | None = Field(
        default=None,
        alias="headMotion",
        serialization_alias="headMotion",
    )
    gaze: GazeTarget | None = None


class AnimationPlanSchema(BaseModel):
    """Plan payload shared by web and future mobile clients."""

    model_config = ConfigDict(ser_json_by_alias=True)

    segments: list[AnimationSegmentSchema]


class GeneratePlanTextRequest(BaseModel):
    """Request body for LLM-backed presenter script text."""

    topic: str = Field(..., min_length=1, max_length=500)


class GeneratePlanTextResponse(BaseModel):
    """Plain-text script to drive a later AnimationPlan step."""

    text: str


class GeneratePlanRequest(BaseModel):
    """Request body for LLM-backed semantic AnimationPlan generation."""

    topic: str = Field(..., min_length=1, max_length=500)


class ChatHistoryMessage(BaseModel):
    """One prior chat turn (user or assistant)."""

    role: Literal["user", "assistant"]
    content: str = Field(..., min_length=1, max_length=2000)


class ChatTurnRequest(BaseModel):
    """One user utterance, optionally with prior conversation turns."""

    message: str = Field(..., min_length=1, max_length=2000)
    history: list[ChatHistoryMessage] = Field(default_factory=list, max_length=20)


class ChatTurnResponse(BaseModel):
    """Assistant reply text for the avatar / chat UI."""

    reply: str


class SynthesizeSpeechRequest(BaseModel):
    """Request body for TTS synthesis."""

    model_config = ConfigDict(populate_by_name=True)

    text: str = Field(..., min_length=1, max_length=4000)
    voice_id: str | None = Field(default=None, alias="voiceId", max_length=64)


class SynthesizeSpeechResponse(BaseModel):
    """Playable audio URL (relative) plus estimated duration."""

    model_config = ConfigDict(populate_by_name=True, ser_json_by_alias=True)

    audio_url: str = Field(alias="audioUrl", serialization_alias="audioUrl")
    duration_seconds: float = Field(
        alias="durationSeconds",
        serialization_alias="durationSeconds",
    )
