"""Create or replace a named animation Action on the presenter armature.

Prefer TypeScript / JSON for simple procedural motion when the runtime can do
it. Use this script for contract-named clips that must exist inside the GLB.

Supported clip names are those in ``contracts.REQUIRED_ANIMATIONS`` and
``contracts.OPTIONAL_ANIMATIONS``. Motions are simple teaching stubs (not
art-directed performance).

List actions:

    blender --background blender/source/presenter.blend --python blender/scripts/create_animation.py -- --list

Create one clip:

    blender --background blender/source/presenter.blend --python blender/scripts/create_animation.py -- --create Idle_Breathing

Overwrite an existing clip:

    blender --background blender/source/presenter.blend --python blender/scripts/create_animation.py -- --create Blink --overwrite

Default flow: backup → create action → NLA stash → save → validate_rig → temp export.
"""

from __future__ import annotations

import argparse
import importlib.util
import math
import sys
from pathlib import Path


def _load_common():
    """Load ``common.py`` from the same scripts directory (works inside Blender)."""
    scripts_dir = Path(__file__).resolve().parent
    spec = importlib.util.spec_from_file_location("common", scripts_dir / "common.py")
    if spec is None or spec.loader is None:
        raise RuntimeError("Unable to load blender/scripts/common.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _script_argv(argv: list[str] | None = None) -> list[str]:
    """Return arguments after ``--`` when launched via ``blender --python``."""
    args = list(sys.argv if argv is None else argv)
    if "--" in args:
        return args[args.index("--") + 1 :]
    return args[1:]


def _allowed_clip_names(contracts) -> set[str]:
    """Return the set of contract animation names."""
    return set(contracts.REQUIRED_ANIMATIONS) | set(contracts.OPTIONAL_ANIMATIONS)


def _find_armature(bpy):
    """Return the first armature object or None."""
    for obj in bpy.data.objects:
        if obj.type == "ARMATURE":
            return obj
    return None


def _find_shape_mesh(bpy):
    """Return the first mesh that has non-Basis shape keys, if any."""
    for obj in bpy.data.objects:
        if obj.type != "MESH" or obj.data.shape_keys is None:
            continue
        names = [kb.name for kb in obj.data.shape_keys.key_blocks]
        if any(n != "Basis" for n in names):
            return obj
    return None


def _bone_exists(arm, name: str) -> bool:
    """Return True if the armature has a bone named ``name``."""
    return name in arm.data.bones


def _clear_action_users(bpy, action) -> None:
    """Detach an action from objects/NLA so it can be removed safely."""
    for obj in bpy.data.objects:
        anim = obj.animation_data
        if anim is None:
            continue
        if anim.action == action:
            anim.action = None
        if anim.nla_tracks:
            for track in list(anim.nla_tracks):
                for strip in list(track.strips):
                    if strip.action == action:
                        track.strips.remove(strip)
                if len(track.strips) == 0:
                    anim.nla_tracks.remove(track)
    for key in bpy.data.shape_keys:
        anim = key.animation_data
        if anim is not None and anim.action == action:
            anim.action = None


def _ensure_action(bpy, name: str, overwrite: bool):
    """Create a new action, or replace an existing one when overwrite is set."""
    existing = bpy.data.actions.get(name)
    if existing is not None:
        if not overwrite:
            raise RuntimeError(
                f"Action already exists: {name}. Pass --overwrite to replace it."
            )
        _clear_action_users(bpy, existing)
        bpy.data.actions.remove(existing)
    return bpy.data.actions.new(name)


def _action_fcurve_count(action) -> int:
    """Count fcurves on legacy or Blender 5 layered actions."""
    fcurves = getattr(action, "fcurves", None)
    if fcurves is not None:
        return len(fcurves)

    total = 0
    slots = list(getattr(action, "slots", []) or [])
    for layer in getattr(action, "layers", []) or []:
        for strip in getattr(layer, "strips", []) or []:
            if not slots:
                continue
            for slot in slots:
                try:
                    bag = strip.channelbag(slot)
                except TypeError:
                    try:
                        bag = strip.channelbag(slot=slot)
                    except Exception:
                        bag = None
                if bag is not None and hasattr(bag, "fcurves"):
                    total += len(bag.fcurves)
    return total


def _assign_nla_slot(strip, action) -> None:
    """Bind a Blender 5 action slot on an NLA strip when required for export."""
    suitable = list(getattr(strip, "action_suitable_slots", []) or [])
    if suitable:
        strip.action_slot = suitable[0]
        return
    slots = list(getattr(action, "slots", []) or [])
    if slots:
        strip.action_slot = slots[0]


def _stash_nla(owner, action) -> None:
    """Place the action on an NLA track on ``owner`` (armature or Key)."""
    owner.animation_data_create()
    anim = owner.animation_data
    for track in list(anim.nla_tracks):
        if track.name == action.name:
            anim.nla_tracks.remove(track)
    track = anim.nla_tracks.new()
    track.name = action.name
    strip = track.strips.new(action.name, 1, action)
    _assign_nla_slot(strip, action)


def _pose_bone(arm, name: str):
    """Return a pose bone or raise."""
    bone = arm.pose.bones.get(name)
    if bone is None:
        raise RuntimeError(f"Pose bone missing: {name}")
    bone.rotation_mode = "XYZ"
    return bone


def _build_bone_clip(bpy, arm, name: str, action) -> None:
    """Populate a pose-bone stub clip for a Mixamo-style T-pose rest.

    Identity euler ``(0,0,0)`` is the bind/T-pose (arms out). Motions use
    small rotation deltas only — never bone location keys (those tear skin).
    Do not reuse hang-arm stand-in angles (e.g. 160°+ Z raises).
    """
    deg = math.radians
    arm.animation_data_create()
    arm.animation_data.action = action
    bpy.context.view_layer.objects.active = arm
    if arm.mode != "POSE":
        bpy.ops.object.mode_set(mode="POSE")
    # Clear leftover pose so keys start from true rest.
    bpy.ops.pose.select_all(action="SELECT")
    bpy.ops.pose.transforms_clear()

    def need(*bones: str) -> None:
        missing = [b for b in bones if not _bone_exists(arm, b)]
        if missing:
            raise RuntimeError(f"Clip {name} needs bones: {', '.join(missing)}")

    def key_rot(bone_name: str, frame: int, euler) -> None:
        bone = _pose_bone(arm, bone_name)
        bone.rotation_euler = euler
        bone.keyframe_insert(data_path="rotation_euler", frame=frame)

    # --- Idles / head (safe on any humanoid) ---
    if name == "Idle_Neutral":
        need("Hips", "Head")
        key_rot("Hips", 1, (0, 0, 0))
        key_rot("Hips", 40, (0, 0, 0))
        key_rot("Head", 1, (0, 0, 0))
        key_rot("Head", 40, (0, 0, 0))
    elif name == "Idle_Breathing":
        bone = "Chest" if _bone_exists(arm, "Chest") else "Spine"
        need(bone)
        key_rot(bone, 1, (0, 0, 0))
        key_rot(bone, 20, (deg(3), 0, 0))
        key_rot(bone, 40, (0, 0, 0))
    elif name == "Idle_AtEase":
        # Mixamo T-pose → arms hang vertically by the sides (local +X on UpperArm),
        # not Z-swing (that puts hands behind the torso). Soft chest breath loop.
        need(
            "LeftUpperArm",
            "RightUpperArm",
            "LeftLowerArm",
            "RightLowerArm",
            "Chest",
        )
        chest = "Chest" if _bone_exists(arm, "Chest") else "Spine"
        for frame, chest_x in ((1, 0.0), (30, 2.5), (60, 0.0)):
            key_rot(chest, frame, (deg(chest_x), 0, 0))
            # +X lowers arms; -Y (mirrored) brings hands slightly forward so they
            # clear the hip mesh (|hand.x| must exceed hip half-width ~0.17).
            key_rot("RightUpperArm", frame, (deg(82), deg(-10), 0))
            key_rot("LeftUpperArm", frame, (deg(82), deg(10), 0))
            key_rot("RightLowerArm", frame, (deg(8), 0, 0))
            key_rot("LeftLowerArm", frame, (deg(8), 0, 0))
    elif name == "Idle_ShiftWeight":
        need("Hips")
        key_rot("Hips", 1, (0, 0, deg(-2)))
        key_rot("Hips", 30, (0, 0, deg(2)))
        key_rot("Hips", 60, (0, 0, deg(-2)))
    elif name == "Idle_StandAttention":
        need("Spine", "Chest", "Head")
        key_rot("Spine", 1, (0, 0, 0))
        key_rot("Chest", 1, (0, 0, 0))
        key_rot("Head", 1, (0, 0, 0))
        key_rot("Spine", 60, (deg(1), 0, 0))
        key_rot("Chest", 60, (deg(2), 0, 0))
        key_rot("Spine", 120, (0, 0, 0))
        key_rot("Chest", 120, (0, 0, 0))
        key_rot("Head", 120, (0, 0, 0))
    elif name == "Idle_AdjustPosture":
        need("Hips", "Spine", "Chest")
        key_rot("Hips", 1, (0, 0, 0))
        key_rot("Hips", 24, (0, 0, deg(3)))
        key_rot("Hips", 54, (0, 0, deg(-2)))
        key_rot("Hips", 90, (0, 0, 0))
        key_rot("Spine", 1, (0, 0, 0))
        key_rot("Spine", 30, (deg(2), 0, 0))
        key_rot("Spine", 90, (0, 0, 0))
        key_rot("Chest", 1, (0, 0, 0))
        key_rot("Chest", 36, (deg(2), 0, 0))
        key_rot("Chest", 90, (0, 0, 0))
    elif name == "Head_Nod_Small":
        need("Head")
        key_rot("Head", 1, (0, 0, 0))
        key_rot("Head", 8, (deg(14), 0, 0))
        key_rot("Head", 14, (deg(-3), 0, 0))
        key_rot("Head", 20, (0, 0, 0))
    elif name == "Head_Turn_Left":
        need("Head")
        key_rot("Head", 1, (0, 0, 0))
        key_rot("Head", 15, (0, deg(-18), 0))
        key_rot("Head", 30, (0, 0, 0))
    elif name == "Head_Turn_Right":
        need("Head")
        key_rot("Head", 1, (0, 0, 0))
        key_rot("Head", 15, (0, deg(18), 0))
        key_rot("Head", 30, (0, 0, 0))
    elif name == "Head_Tilt_Left":
        need("Head")
        key_rot("Head", 1, (0, 0, 0))
        key_rot("Head", 15, (0, 0, deg(12)))
        key_rot("Head", 30, (0, 0, 0))
    elif name == "Head_Tilt_Right":
        need("Head")
        key_rot("Head", 1, (0, 0, 0))
        key_rot("Head", 15, (0, 0, deg(-12)))
        key_rot("Head", 30, (0, 0, 0))
    elif name == "Head_Shake":
        need("Head")
        key_rot("Head", 1, (0, 0, 0))
        key_rot("Head", 6, (0, deg(14), 0))
        key_rot("Head", 12, (0, deg(-14), 0))
        key_rot("Head", 18, (0, deg(12), 0))
        key_rot("Head", 24, (0, deg(-12), 0))
        key_rot("Head", 30, (0, 0, 0))
    elif name == "Gesture_Nod":
        need("Head")
        key_rot("Head", 1, (0, 0, 0))
        key_rot("Head", 8, (deg(12), 0, 0))
        key_rot("Head", 16, (0, 0, 0))
    # --- Arm gestures: T-pose deltas (lift / bend, never 90°+ twist from hang) ---
    elif name == "Gesture_OpenHand":
        need("RightUpperArm", "RightLowerArm", "RightHand")
        key_rot("RightUpperArm", 1, (0, 0, 0))
        key_rot("RightLowerArm", 1, (0, 0, 0))
        key_rot("RightHand", 1, (0, 0, 0))
        key_rot("RightUpperArm", 12, (deg(-20), deg(-8), deg(-12)))
        key_rot("RightLowerArm", 12, (deg(-35), 0, 0))
        key_rot("RightHand", 12, (deg(-8), 0, deg(8)))
        key_rot("RightUpperArm", 28, (0, 0, 0))
        key_rot("RightLowerArm", 28, (0, 0, 0))
        key_rot("RightHand", 28, (0, 0, 0))
    elif name == "Gesture_Emphasize":
        need("RightUpperArm", "RightLowerArm", "RightHand")
        key_rot("RightUpperArm", 1, (0, 0, 0))
        key_rot("RightLowerArm", 1, (0, 0, 0))
        key_rot("RightHand", 1, (0, 0, 0))
        key_rot("RightUpperArm", 8, (deg(-22), deg(-5), deg(-10)))
        key_rot("RightLowerArm", 8, (deg(-40), 0, 0))
        key_rot("RightHand", 8, (deg(-10), 0, deg(-6)))
        key_rot("RightUpperArm", 16, (deg(-12), 0, deg(-4)))
        key_rot("RightLowerArm", 16, (deg(-20), 0, 0))
        key_rot("RightHand", 16, (deg(6), 0, 0))
        key_rot("RightUpperArm", 28, (0, 0, 0))
        key_rot("RightLowerArm", 28, (0, 0, 0))
        key_rot("RightHand", 28, (0, 0, 0))
    elif name == "Gesture_PointLeft":
        need("LeftUpperArm", "LeftLowerArm", "LeftHand")
        key_rot("LeftUpperArm", 1, (0, 0, 0))
        key_rot("LeftLowerArm", 1, (0, 0, 0))
        key_rot("LeftHand", 1, (0, 0, 0))
        key_rot("LeftUpperArm", 12, (deg(-18), deg(8), deg(18)))
        key_rot("LeftLowerArm", 12, (deg(-28), 0, 0))
        key_rot("LeftHand", 12, (0, deg(-10), deg(12)))
        key_rot("LeftUpperArm", 28, (0, 0, 0))
        key_rot("LeftLowerArm", 28, (0, 0, 0))
        key_rot("LeftHand", 28, (0, 0, 0))
    elif name == "Gesture_PointRight":
        need("RightUpperArm", "RightLowerArm", "RightHand")
        key_rot("RightUpperArm", 1, (0, 0, 0))
        key_rot("RightLowerArm", 1, (0, 0, 0))
        key_rot("RightHand", 1, (0, 0, 0))
        key_rot("RightUpperArm", 12, (deg(-18), deg(-8), deg(-18)))
        key_rot("RightLowerArm", 12, (deg(-28), 0, 0))
        key_rot("RightHand", 12, (0, deg(10), deg(-12)))
        key_rot("RightUpperArm", 28, (0, 0, 0))
        key_rot("RightLowerArm", 28, (0, 0, 0))
        key_rot("RightHand", 28, (0, 0, 0))
    elif name == "Gesture_HandsTogether":
        need(
            "LeftUpperArm",
            "LeftLowerArm",
            "LeftHand",
            "RightUpperArm",
            "RightLowerArm",
            "RightHand",
        )
        for side in ("Left", "Right"):
            key_rot(f"{side}UpperArm", 1, (0, 0, 0))
            key_rot(f"{side}LowerArm", 1, (0, 0, 0))
            key_rot(f"{side}Hand", 1, (0, 0, 0))
        key_rot("LeftUpperArm", 14, (deg(-22), deg(10), deg(22)))
        key_rot("LeftLowerArm", 14, (deg(-40), 0, 0))
        key_rot("LeftHand", 14, (deg(-6), 0, deg(8)))
        key_rot("RightUpperArm", 14, (deg(-22), deg(-10), deg(-22)))
        key_rot("RightLowerArm", 14, (deg(-40), 0, 0))
        key_rot("RightHand", 14, (deg(-6), 0, deg(-8)))
        for side in ("Left", "Right"):
            key_rot(f"{side}UpperArm", 32, (0, 0, 0))
            key_rot(f"{side}LowerArm", 32, (0, 0, 0))
            key_rot(f"{side}Hand", 32, (0, 0, 0))
    elif name == "Gesture_Wave":
        # Elbow-driven wave from T-pose; keep upper-arm deltas small.
        need("RightUpperArm", "RightLowerArm", "RightHand")
        key_rot("RightUpperArm", 1, (0, 0, 0))
        key_rot("RightLowerArm", 1, (0, 0, 0))
        key_rot("RightHand", 1, (0, 0, 0))
        key_rot("RightUpperArm", 10, (deg(-15), 0, deg(-20)))
        key_rot("RightLowerArm", 10, (deg(-45), 0, 0))
        key_rot("RightHand", 16, (0, 0, deg(18)))
        key_rot("RightHand", 22, (0, 0, deg(-18)))
        key_rot("RightHand", 28, (0, 0, deg(18)))
        key_rot("RightHand", 34, (0, 0, deg(-18)))
        key_rot("RightUpperArm", 44, (0, 0, 0))
        key_rot("RightLowerArm", 44, (0, 0, 0))
        key_rot("RightHand", 44, (0, 0, 0))
    elif name == "Gesture_RaiseHand":
        need("RightUpperArm", "RightLowerArm")
        key_rot("RightUpperArm", 1, (0, 0, 0))
        key_rot("RightLowerArm", 1, (0, 0, 0))
        key_rot("RightUpperArm", 14, (deg(-25), 0, deg(-35)))
        key_rot("RightLowerArm", 14, (deg(-20), 0, 0))
        key_rot("RightUpperArm", 36, (deg(-25), 0, deg(-35)))
        key_rot("RightLowerArm", 36, (deg(-20), 0, 0))
        key_rot("RightUpperArm", 48, (0, 0, 0))
        key_rot("RightLowerArm", 48, (0, 0, 0))
    elif name == "Gesture_RaiseHandLeft":
        need("LeftUpperArm", "LeftLowerArm")
        key_rot("LeftUpperArm", 1, (0, 0, 0))
        key_rot("LeftLowerArm", 1, (0, 0, 0))
        key_rot("LeftUpperArm", 14, (deg(-25), 0, deg(35)))
        key_rot("LeftLowerArm", 14, (deg(-20), 0, 0))
        key_rot("LeftUpperArm", 36, (deg(-25), 0, deg(35)))
        key_rot("LeftLowerArm", 36, (deg(-20), 0, 0))
        key_rot("LeftUpperArm", 48, (0, 0, 0))
        key_rot("LeftLowerArm", 48, (0, 0, 0))
    elif name == "Gesture_BothHands":
        need("LeftUpperArm", "RightUpperArm", "LeftLowerArm", "RightLowerArm")
        for side, z in (("Left", 1), ("Right", -1)):
            key_rot(f"{side}UpperArm", 1, (0, 0, 0))
            key_rot(f"{side}LowerArm", 1, (0, 0, 0))
            key_rot(f"{side}UpperArm", 14, (deg(-22), 0, deg(30 * z)))
            key_rot(f"{side}LowerArm", 14, (deg(-18), 0, 0))
            key_rot(f"{side}UpperArm", 36, (deg(-22), 0, deg(30 * z)))
            key_rot(f"{side}LowerArm", 36, (deg(-18), 0, 0))
            key_rot(f"{side}UpperArm", 48, (0, 0, 0))
            key_rot(f"{side}LowerArm", 48, (0, 0, 0))
    elif name == "Gesture_Shrug":
        need("LeftShoulder", "RightShoulder", "LeftUpperArm", "RightUpperArm")
        key_rot("LeftShoulder", 1, (0, 0, 0))
        key_rot("RightShoulder", 1, (0, 0, 0))
        key_rot("LeftUpperArm", 1, (0, 0, 0))
        key_rot("RightUpperArm", 1, (0, 0, 0))
        key_rot("LeftShoulder", 10, (0, 0, deg(12)))
        key_rot("RightShoulder", 10, (0, 0, deg(-12)))
        key_rot("LeftUpperArm", 10, (deg(-8), deg(4), deg(-10)))
        key_rot("RightUpperArm", 10, (deg(-8), deg(-4), deg(10)))
        key_rot("LeftShoulder", 28, (0, 0, deg(12)))
        key_rot("RightShoulder", 28, (0, 0, deg(-12)))
        key_rot("LeftShoulder", 40, (0, 0, 0))
        key_rot("RightShoulder", 40, (0, 0, 0))
        key_rot("LeftUpperArm", 40, (0, 0, 0))
        key_rot("RightUpperArm", 40, (0, 0, 0))
    elif name == "Gesture_LeanForward":
        need("Spine", "Chest", "Head")
        key_rot("Spine", 1, (0, 0, 0))
        key_rot("Chest", 1, (0, 0, 0))
        key_rot("Head", 1, (0, 0, 0))
        key_rot("Spine", 12, (deg(8), 0, 0))
        key_rot("Chest", 12, (deg(6), 0, 0))
        key_rot("Head", 12, (deg(4), 0, 0))
        key_rot("Spine", 36, (deg(8), 0, 0))
        key_rot("Chest", 36, (deg(6), 0, 0))
        key_rot("Head", 36, (deg(4), 0, 0))
        key_rot("Spine", 48, (0, 0, 0))
        key_rot("Chest", 48, (0, 0, 0))
        key_rot("Head", 48, (0, 0, 0))
    elif name == "Gesture_LeanBack":
        need("Spine", "Chest", "Head")
        key_rot("Spine", 1, (0, 0, 0))
        key_rot("Chest", 1, (0, 0, 0))
        key_rot("Head", 1, (0, 0, 0))
        key_rot("Spine", 12, (deg(-6), 0, 0))
        key_rot("Chest", 12, (deg(-5), 0, 0))
        key_rot("Head", 12, (deg(-3), 0, 0))
        key_rot("Spine", 36, (deg(-6), 0, 0))
        key_rot("Chest", 36, (deg(-5), 0, 0))
        key_rot("Head", 36, (deg(-3), 0, 0))
        key_rot("Spine", 48, (0, 0, 0))
        key_rot("Chest", 48, (0, 0, 0))
        key_rot("Head", 48, (0, 0, 0))
    elif name == "Turn_Body_Left":
        need("Hips", "Spine", "Chest")
        key_rot("Hips", 1, (0, 0, 0))
        key_rot("Spine", 1, (0, 0, 0))
        key_rot("Chest", 1, (0, 0, 0))
        key_rot("Hips", 16, (0, deg(-12), 0))
        key_rot("Spine", 16, (0, deg(-8), 0))
        key_rot("Chest", 16, (0, deg(-5), 0))
        key_rot("Hips", 36, (0, 0, 0))
        key_rot("Spine", 36, (0, 0, 0))
        key_rot("Chest", 36, (0, 0, 0))
    elif name == "Turn_Body_Right":
        need("Hips", "Spine", "Chest")
        key_rot("Hips", 1, (0, 0, 0))
        key_rot("Spine", 1, (0, 0, 0))
        key_rot("Chest", 1, (0, 0, 0))
        key_rot("Hips", 16, (0, deg(12), 0))
        key_rot("Spine", 16, (0, deg(8), 0))
        key_rot("Chest", 16, (0, deg(5), 0))
        key_rot("Hips", 36, (0, 0, 0))
        key_rot("Spine", 36, (0, 0, 0))
        key_rot("Chest", 36, (0, 0, 0))
    elif name == "Walk_Forward":
        need("Hips", "LeftUpperLeg", "RightUpperLeg", "LeftUpperArm", "RightUpperArm")
        key_rot("Hips", 1, (0, 0, 0))
        key_rot("LeftUpperLeg", 1, (0, 0, 0))
        key_rot("RightUpperLeg", 1, (0, 0, 0))
        key_rot("LeftUpperArm", 1, (0, 0, 0))
        key_rot("RightUpperArm", 1, (0, 0, 0))
        key_rot("Hips", 12, (deg(2), 0, deg(2)))
        key_rot("LeftUpperLeg", 12, (deg(18), 0, 0))
        key_rot("RightUpperLeg", 12, (deg(-12), 0, 0))
        key_rot("LeftUpperArm", 12, (deg(-8), 0, deg(-6)))
        key_rot("RightUpperArm", 12, (deg(6), 0, deg(6)))
        key_rot("Hips", 24, (deg(2), 0, deg(-2)))
        key_rot("LeftUpperLeg", 24, (deg(-12), 0, 0))
        key_rot("RightUpperLeg", 24, (deg(18), 0, 0))
        key_rot("LeftUpperArm", 24, (deg(6), 0, deg(6)))
        key_rot("RightUpperArm", 24, (deg(-8), 0, deg(6)))
        key_rot("Hips", 36, (0, 0, 0))
        key_rot("LeftUpperLeg", 36, (0, 0, 0))
        key_rot("RightUpperLeg", 36, (0, 0, 0))
        key_rot("LeftUpperArm", 36, (0, 0, 0))
        key_rot("RightUpperArm", 36, (0, 0, 0))
    elif name == "Walk_Backward":
        need("Hips", "LeftUpperLeg", "RightUpperLeg", "LeftUpperArm", "RightUpperArm")
        key_rot("Hips", 1, (0, 0, 0))
        key_rot("LeftUpperLeg", 1, (0, 0, 0))
        key_rot("RightUpperLeg", 1, (0, 0, 0))
        key_rot("LeftUpperArm", 1, (0, 0, 0))
        key_rot("RightUpperArm", 1, (0, 0, 0))
        key_rot("Hips", 12, (deg(-2), 0, deg(-2)))
        key_rot("LeftUpperLeg", 12, (deg(-12), 0, 0))
        key_rot("RightUpperLeg", 12, (deg(16), 0, 0))
        key_rot("LeftUpperArm", 12, (deg(6), 0, deg(5)))
        key_rot("RightUpperArm", 12, (deg(-8), 0, deg(5)))
        key_rot("Hips", 24, (deg(-2), 0, deg(2)))
        key_rot("LeftUpperLeg", 24, (deg(16), 0, 0))
        key_rot("RightUpperLeg", 24, (deg(-12), 0, 0))
        key_rot("LeftUpperArm", 24, (deg(-8), 0, deg(-5)))
        key_rot("RightUpperArm", 24, (deg(6), 0, deg(-5)))
        key_rot("Hips", 36, (0, 0, 0))
        key_rot("LeftUpperLeg", 36, (0, 0, 0))
        key_rot("RightUpperLeg", 36, (0, 0, 0))
        key_rot("LeftUpperArm", 36, (0, 0, 0))
        key_rot("RightUpperArm", 36, (0, 0, 0))
    else:
        raise RuntimeError(f"Not a bone stub clip: {name}")

    bpy.ops.object.mode_set(mode="OBJECT")
    arm.animation_data.action = None
    _stash_nla(arm, action)


def _build_shape_clip(mesh, name: str, action) -> None:
    """Populate a shape-key stub clip on the mesh Key data-block."""
    key = mesh.data.shape_keys
    if key is None:
        raise RuntimeError(f"{name} requires shape keys on {mesh.name}")

    key.animation_data_create()
    key.animation_data.action = action

    def key_shape(shape_name: str, frame: int, value: float) -> None:
        block = key.key_blocks.get(shape_name)
        if block is None:
            raise RuntimeError(f"Shape key missing on {mesh.name}: {shape_name}")
        block.value = value
        block.keyframe_insert(data_path="value", frame=frame)

    if name == "Blink":
        for frame, value in ((1, 0.0), (3, 1.0), (6, 0.0)):
            key_shape("eye_blink_left", frame, value)
            key_shape("eye_blink_right", frame, value)
        return

    mapping = {
        "Emotion_Neutral": [],
        "Emotion_Serious": [("brow_down", 0.6), ("mouth_frown", 0.3)],
        "Emotion_Positive": [("mouth_smile", 0.7), ("brow_up", 0.2)],
        "Emotion_Concerned": [("brow_up", 0.5), ("mouth_frown", 0.4)],
    }
    if name not in mapping:
        raise RuntimeError(f"Not a shape-key stub clip: {name}")

    shapes = mapping[name]
    if not shapes:
        # Neutral hold: drive mouth_close if present, else first available key
        fallback = "mouth_close" if "mouth_close" in key.key_blocks else None
        if fallback:
            key_shape(fallback, 1, 0.0)
            key_shape(fallback, 20, 0.0)
        else:
            raise RuntimeError("Emotion_Neutral needs at least one facial shape key")
        return

    for shape_name, peak in shapes:
        key_shape(shape_name, 1, 0.0)
        key_shape(shape_name, 15, peak)
        key_shape(shape_name, 30, 0.0)


def _list_actions(bpy, emit) -> int:
    """Print actions and NLA strip names."""
    emit("SECTION", "actions")
    actions = sorted(bpy.data.actions, key=lambda a: a.name)
    if not actions:
        emit("INFO", "No actions in bpy.data.actions.")
    for action in actions:
        emit("ACTION", f"{action.name}|fcurves={_action_fcurve_count(action)}")

    emit("SECTION", "nla")
    arm = _find_armature(bpy)
    if arm is None or arm.animation_data is None:
        emit("INFO", "No armature NLA data.")
    else:
        for track in arm.animation_data.nla_tracks:
            for strip in track.strips:
                action_name = strip.action.name if strip.action else "-"
                emit("NLA_STRIP", f"{track.name}|strip={strip.name}|action={action_name}")

    emit("COUNT", f"actions={len(actions)}")
    emit("RESULT", "OK")
    return 0


def _build_parser() -> argparse.ArgumentParser:
    """Create CLI parser for animation creation."""
    parser = argparse.ArgumentParser(
        description="Create contract-named stub animation clips on the presenter armature.",
    )
    parser.add_argument("--list", action="store_true", help="List actions / NLA strips and exit.")
    parser.add_argument(
        "--create",
        type=str,
        default=None,
        help="Contract animation name to create (see contracts.py).",
    )
    parser.add_argument(
        "--create-all-required",
        action="store_true",
        help="Create every contracts.REQUIRED_ANIMATIONS clip (uses --overwrite).",
    )
    parser.add_argument(
        "--create-all-optional",
        action="store_true",
        help="Create every contracts.OPTIONAL_ANIMATIONS clip (uses --overwrite).",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Replace an existing action with the same name.",
    )
    parser.add_argument("--no-backup", action="store_true", help="Skip versioned backup.")
    parser.add_argument("--skip-validate", action="store_true", help="Skip validate_rig.")
    parser.add_argument("--skip-export", action="store_true", help="Skip temp GLB export.")
    return parser


SHAPE_CLIPS = {
    "Blink",
    "Emotion_Neutral",
    "Emotion_Serious",
    "Emotion_Positive",
    "Emotion_Concerned",
}


def _create_one(bpy, arm, mesh, clip_name: str, overwrite: bool, report) -> None:
    """Create a single stub clip by name."""
    action = _ensure_action(bpy, clip_name, overwrite)
    if clip_name in SHAPE_CLIPS:
        if mesh is None:
            raise RuntimeError(f"{clip_name} requires a mesh with shape keys")
        _build_shape_clip(mesh, clip_name, action)
        # Shape-key actions must live on the Key data-block (not armature NLA)
        # so the glTF exporter can find morph animation slots.
        key = mesh.data.shape_keys
        key.animation_data_create()
        key.animation_data.action = None
        _stash_nla(key, action)
    else:
        _build_bone_clip(bpy, arm, clip_name, action)
    report("PASS", f"Created action: {clip_name} (fcurves={_action_fcurve_count(action)})")


def create_animation(argv: list[str] | None = None) -> int:
    """List or create stub animation clip(s); return process exit code."""
    try:
        return _create_animation_impl(argv)
    except Exception as exc:  # noqa: BLE001 - surface unexpected bpy/API failures
        print(f"ERROR: {exc}")
        print("RESULT: ERROR")
        return 1


def _create_animation_impl(argv: list[str] | None = None) -> int:
    """Implementation of create_animation with typed failures as return codes."""
    common = _load_common()
    bpy = common.require_bpy()
    emit = common.emit
    report = common.report
    contracts = common.load_scripts_module("contracts")

    parser = _build_parser()
    try:
        args = parser.parse_args(_script_argv(argv))
    except SystemExit as exc:
        return exc.code if isinstance(exc.code, int) else 1

    blend_path = bpy.data.filepath or "(unsaved / default startup)"
    emit("FILE", blend_path)

    if args.list:
        return _list_actions(bpy, emit)

    if not args.create and not args.create_all_required and not args.create_all_optional:
        report(
            "ERROR",
            "Provide --create CLIP_NAME, --create-all-required, "
            "--create-all-optional, or --list.",
        )
        emit("RESULT", "ERROR")
        return 1

    arm = _find_armature(bpy)
    if arm is None:
        report("ERROR", "No armature in the file. Run scaffold_presenter_blend.py or import a character first.")
        emit("RESULT", "ERROR")
        return 1

    mesh = _find_shape_mesh(bpy)
    report("INFO", f"Armature: {arm.name}")
    report("INFO", f"Shape mesh: {mesh.name if mesh else '(none)'}")

    clips: list[str] = []
    overwrite = args.overwrite
    if args.create_all_required:
        clips.extend(contracts.REQUIRED_ANIMATIONS)
        overwrite = True
    if args.create_all_optional:
        clips.extend(contracts.OPTIONAL_ANIMATIONS)
        overwrite = True
    if args.create:
        clip_name = args.create
        allowed = _allowed_clip_names(contracts)
        if clip_name not in allowed:
            report("ERROR", f"Unknown clip (not in contracts): {clip_name}")
            report("INFO", "Allowed: " + ", ".join(sorted(allowed)))
            emit("RESULT", "ERROR")
            return 1
        if clip_name not in clips:
            clips.append(clip_name)

    # Deduplicate while preserving order
    seen: set[str] = set()
    unique_clips: list[str] = []
    for name in clips:
        if name not in seen:
            seen.add(name)
            unique_clips.append(name)
    clips = unique_clips

    if args.no_backup:
        report("WARNING", "Skipping versioned backup (--no-backup).")
    else:
        try:
            if args.create_all_required and args.create_all_optional:
                label = "pre_anim_all_contract"
            elif args.create_all_required:
                label = "pre_anim_all_required"
            elif args.create_all_optional:
                label = "pre_anim_all_optional"
            else:
                label = f"pre_anim_{clips[0]}"
            common.save_versioned_blend(label=label)
        except RuntimeError as exc:
            report("ERROR", str(exc))
            emit("RESULT", "ERROR")
            return 1

    try:
        for clip_name in clips:
            if clip_name in SHAPE_CLIPS and mesh is None:
                report(
                    "WARNING",
                    f"Skipping {clip_name} (no facial shape keys on this character).",
                )
                continue
            _create_one(bpy, arm, mesh, clip_name, overwrite, report)
    except RuntimeError as exc:
        report("ERROR", str(exc))
        emit("RESULT", "ERROR")
        return 1

    # Shape-key clip authoring leaves key_block.value at the last keyframe.
    # Reset so the rest pose is clean in the .blend (and for later transforms).
    if mesh is not None and mesh.data.shape_keys is not None:
        for block in mesh.data.shape_keys.key_blocks:
            if block.name != "Basis":
                block.value = 0.0
        report("PASS", "Zeroed shape-key values after clip create")

    if bpy.data.filepath:
        bpy.ops.wm.save_mainfile()
        report("PASS", f"Saved working blend: {bpy.data.filepath}")
    else:
        report("WARNING", "Working blend is unsaved.")

    if not args.skip_validate:
        validate_rig = common.load_scripts_module("validate_rig")
        report("INFO", "Running validate_rig...")
        if validate_rig.validate() != 0:
            report("ERROR", "validate_rig failed after animation create. Export skipped.")
            emit("RESULT", "ERROR")
            return 1
    else:
        report("WARNING", "Skipped validate_rig (--skip-validate).")

    if not args.skip_export:
        export_glb = common.load_scripts_module("export_glb")
        report("INFO", "Exporting to temp GLB...")
        if export_glb.export() != 0:
            report("ERROR", "Temp export failed.")
            emit("RESULT", "ERROR")
            return 1
        report(
            "INFO",
            "Next: python blender/scripts/validate_export.py "
            "then python blender/scripts/promote_export.py",
        )
    else:
        report("WARNING", "Skipped temp export (--skip-export).")

    emit("RESULT", "OK")
    return 0


if __name__ == "__main__":
    sys.exit(create_animation())
