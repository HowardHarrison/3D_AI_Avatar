"""Validate presenter.blend against the Phase 1 avatar contract.

Run inside Blender:

    blender --background blender/source/presenter.blend --python blender/scripts/validate_rig.py

Exit codes: 0 if no ERROR results, 1 otherwise. Missing optional clips are WARNING.
"""

from __future__ import annotations

import importlib.util
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


def validate() -> int:
    """Inspect the open Blender file and return the process exit code."""
    common = _load_common()
    bpy = common.require_bpy()
    report = common.report

    contracts = common.load_scripts_module("contracts")
    errors = 0
    warnings = 0

    objects = list(bpy.data.objects)
    if not objects:
        report("ERROR", "No objects in the file (avatar missing).")
        return 1
    report("PASS", f"Found {len(objects)} object(s).")

    armatures = [obj for obj in objects if obj.type == "ARMATURE"]
    if not armatures:
        report("ERROR", "No armature found.")
        errors += 1
        armature = None
    else:
        armature = armatures[0]
        report("PASS", f"Armature exists: {armature.name}")
        bone_names = {bone.name for bone in armature.data.bones}
        for bone in contracts.REQUIRED_BONES:
            if bone in bone_names:
                report("PASS", f"Bone present: {bone}")
            else:
                report("ERROR", f"Required bone missing: {bone}")
                errors += 1
        for bone in contracts.OPTIONAL_BODY_BONES:
            if bone not in bone_names:
                report("WARNING", f"Optional bone missing: {bone}")
                warnings += 1

        finger_present = [b for b in contracts.OPTIONAL_FINGER_BONES if b in bone_names]
        if not finger_present:
            report(
                "WARNING",
                "Optional finger bones not present (expected after Mixamo rename).",
            )
            warnings += 1
        else:
            for bone in contracts.OPTIONAL_FINGER_BONES:
                if bone in bone_names:
                    report("PASS", f"Finger bone present: {bone}")
                else:
                    report("WARNING", f"Optional finger bone missing: {bone}")
                    warnings += 1

    meshes = [obj for obj in objects if obj.type == "MESH"]
    if not meshes:
        report("ERROR", "No mesh objects found.")
        errors += 1
    else:
        report("PASS", f"Mesh count: {len(meshes)}")

    shape_keys_found: set[str] = set()
    for mesh_obj in meshes:
        key = mesh_obj.data.shape_keys
        if key is None:
            continue
        for block in key.key_blocks:
            if block.name != "Basis":
                shape_keys_found.add(block.name)

    for name in contracts.REQUIRED_SHAPE_KEYS:
        if name in shape_keys_found:
            report("PASS", f"Shape key present: {name}")
        else:
            report("ERROR", f"Required shape key missing: {name}")
            errors += 1

    optional_face = [n for n in contracts.OPTIONAL_SHAPE_KEYS if n in shape_keys_found]
    if not optional_face:
        report(
            "WARNING",
            "Optional face shape keys not present "
            f"({', '.join(contracts.OPTIONAL_SHAPE_KEYS)}). "
            "Mixamo does not supply these — add in Blender after import.",
        )
        warnings += 1
    else:
        for name in contracts.OPTIONAL_SHAPE_KEYS:
            if name in shape_keys_found:
                report("PASS", f"Optional shape key present: {name}")
            else:
                report("WARNING", f"Optional shape key missing: {name}")
                warnings += 1

    action_names = {action.name for action in bpy.data.actions}
    nla_names: set[str] = set()
    if armature is not None and armature.animation_data and armature.animation_data.nla_tracks:
        for track in armature.animation_data.nla_tracks:
            for strip in track.strips:
                if strip.name:
                    nla_names.add(strip.name)
                if strip.action:
                    action_names.add(strip.action.name)

    clip_names = action_names | nla_names
    if clip_names:
        report("PASS", f"Animation clips found: {len(clip_names)}")
    else:
        report("ERROR", "No animation clips present.")
        errors += 1

    for name in contracts.REQUIRED_ANIMATIONS:
        if name in clip_names:
            report("PASS", f"Animation present: {name}")
        else:
            report("ERROR", f"Required animation missing: {name}")
            errors += 1

    for name in contracts.OPTIONAL_ANIMATIONS:
        if name not in clip_names:
            report("WARNING", f"Optional animation missing: {name}")
            warnings += 1

    materials = list(bpy.data.materials)
    if materials:
        report("PASS", f"Materials exist: {len(materials)}")
    else:
        report("ERROR", "No materials found.")
        errors += 1

    images = [img for img in bpy.data.images if img.size[0] > 0]
    if images:
        report("PASS", f"Textures available: {len(images)}")
    else:
        report("WARNING", "No packed/loaded textures (untextured materials are allowed for MVP).")
        warnings += 1

    if armature is not None:
        world_scale = armature.matrix_world.to_scale()
        if abs(world_scale.x - 1.0) > 0.01 or abs(world_scale.y - 1.0) > 0.01 or abs(world_scale.z - 1.0) > 0.01:
            report("WARNING", "Armature world scale is not 1,1,1. Apply scale before export.")
            warnings += 1
        else:
            report("PASS", "Armature scale is reasonable (approx 1,1,1).")

        loc = armature.matrix_world.to_translation()
        if abs(loc.x) > 0.5 or abs(loc.y) > 0.5:
            report("WARNING", "Armature is offset from origin; presenter may sit off-camera.")
            warnings += 1
        else:
            report("PASS", "Armature is near the world origin.")

    print("---")
    print(f"SUMMARY: errors={errors} warnings={warnings}")
    if errors:
        print("RESULT: ERROR")
        return 1
    print("RESULT: PASS" if warnings == 0 else "RESULT: WARNING")
    return 0


if __name__ == "__main__":
    sys.exit(validate())
