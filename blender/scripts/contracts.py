"""Shared naming contracts for Blender validation, GLB export, and the placeholder generator.

These identifiers must stay stable. The web runtime maps semantic names to these
clip and shape-key strings and must never depend on numeric indexes.
"""

from __future__ import annotations

REQUIRED_BONES: tuple[str, ...] = (
    "Hips",
    "Spine",
    "Chest",
    "Neck",
    "Head",
    "LeftShoulder",
    "LeftUpperArm",
    "LeftLowerArm",
    "LeftHand",
    "RightShoulder",
    "RightUpperArm",
    "RightLowerArm",
    "RightHand",
)

OPTIONAL_BONES: tuple[str, ...] = (
    "LeftUpperLeg",
    "LeftLowerLeg",
    "LeftFoot",
    "RightUpperLeg",
    "RightLowerLeg",
    "RightFoot",
    "LeftEye",
    "RightEye",
)

REQUIRED_SHAPE_KEYS: tuple[str, ...] = (
    "mouth_open",
    "mouth_close",
    "mouth_wide",
    "mouth_round",
    "mouth_smile",
    "mouth_frown",
    "jaw_open",
    "brow_up",
    "brow_down",
    "eye_blink_left",
    "eye_blink_right",
    "eye_wide",
    "eye_squint",
)

REQUIRED_ANIMATIONS: tuple[str, ...] = (
    "Idle_Neutral",
    "Idle_Breathing",
    "Gesture_OpenHand",
    "Gesture_Emphasize",
    "Gesture_PointLeft",
    "Gesture_PointRight",
    "Gesture_HandsTogether",
    "Emotion_Neutral",
    "Emotion_Serious",
    "Emotion_Positive",
    "Emotion_Concerned",
    "Blink",
)

OPTIONAL_ANIMATIONS: tuple[str, ...] = (
    "Idle_ShiftWeight",
    "Head_Nod_Small",
    "Head_Turn_Left",
    "Head_Turn_Right",
    "Head_Tilt_Left",
    "Head_Tilt_Right",
    "Gesture_Nod",
)
