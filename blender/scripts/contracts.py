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

# Legs / eyes — useful for full-body or gaze; not required for bust framing.
OPTIONAL_BODY_BONES: tuple[str, ...] = (
    "LeftUpperLeg",
    "LeftLowerLeg",
    "LeftFoot",
    "RightUpperLeg",
    "RightLowerLeg",
    "RightFoot",
    "LeftEye",
    "RightEye",
)

# Mixamo-style finger chains (3 bones per digit). Optional until a Mixamo-rigged
# character is promoted; the box-head stand-in does not include them.
OPTIONAL_FINGER_BONES: tuple[str, ...] = (
    "LeftHandThumb1",
    "LeftHandThumb2",
    "LeftHandThumb3",
    "LeftHandIndex1",
    "LeftHandIndex2",
    "LeftHandIndex3",
    "LeftHandIndex4",
    "LeftHandMiddle1",
    "LeftHandMiddle2",
    "LeftHandMiddle3",
    "LeftHandRing1",
    "LeftHandRing2",
    "LeftHandRing3",
    "LeftHandPinky1",
    "LeftHandPinky2",
    "LeftHandPinky3",
    "RightHandThumb1",
    "RightHandThumb2",
    "RightHandThumb3",
    "RightHandIndex1",
    "RightHandIndex2",
    "RightHandIndex3",
    "RightHandIndex4",
    "RightHandMiddle1",
    "RightHandMiddle2",
    "RightHandMiddle3",
    "RightHandRing1",
    "RightHandRing2",
    "RightHandRing3",
    "RightHandPinky1",
    "RightHandPinky2",
    "RightHandPinky3",
)

OPTIONAL_BONES: tuple[str, ...] = OPTIONAL_BODY_BONES + OPTIONAL_FINGER_BONES

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

# Extra stylized face shapes for richer presets. Not required on the stand-in;
# Mixamo does not supply these — add them in Blender after import.
OPTIONAL_SHAPE_KEYS: tuple[str, ...] = (
    "brow_inner_up",
    "cheek_raise",
    "mouth_left",
    "mouth_right",
    "nose_sneer",
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
    "Head_Shake",
    "Gesture_Nod",
    "Gesture_BothHands",
)
