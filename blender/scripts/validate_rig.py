"""Validate presenter.blend against the Phase 1 avatar contract.

Run inside Blender:

    blender --background blender/source/presenter.blend --python blender/scripts/validate_rig.py

Exit codes: 0 if no ERROR results, 1 otherwise. Missing optional clips are WARNING.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


def _load_contracts():
    """Load naming contracts from the same scripts directory (works inside Blender)."""
    scripts_dir = Path(__file__).resolve().parent
    spec = importlib.util.spec_from_file_location("contracts", scripts_dir / "contracts.py")
    if spec is None or spec.loader is None:
        raise RuntimeError("Unable to load blender/scripts/contracts.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _report(level: str, message: str) -> None:
    """Print a single validation line with a PASS, WARNING, or ERROR prefix."""
    print(f"{level}: {message}")


def validate() -> int:
    """Inspect the open Blender file and return the process exit code."""
    try:
        import bpy  # type: ignore
    except ImportError:
        _report("ERROR", "This script must run inside Blender (bpy is missing).")
        return 1

    contracts = _load_contracts()
    errors = 0
    warnings = 0

    objects = list(bpy.data.objects)
    if not objects:
        _report("ERROR", "No objects in the file (avatar missing).")
        return 1
    _report("PASS", f"Found {len(objects)} object(s).")

    armatures = [obj for obj in objects if obj.type == "ARMATURE"]
    if not armatures:
        _report("ERROR", "No armature found.")
        errors += 1
        armature = None
    else:
        armature = armatures[0]
        _report("PASS", f"Armature exists: {armature.name}")
        bone_names = {bone.name for bone in armature.data.bones}
        for bone in contracts.REQUIRED_BONES:
            if bone in bone_names:
                _report("PASS", f"Bone present: {bone}")
            else:
                _report("ERROR", f"Required bone missing: {bone}")
                errors += 1
        for bone in contracts.OPTIONAL_BONES:
            if bone not in bone_names:
                _report("WARNING", f"Optional bone missing: {bone}")
                warnings += 1

    meshes = [obj for obj in objects if obj.type == "MESH"]
    if not meshes:
        _report("ERROR", "No mesh objects found.")
        errors += 1
    else:
        _report("PASS", f"Mesh count: {len(meshes)}")

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
            _report("PASS", f"Shape key present: {name}")
        else:
            _report("ERROR", f"Required shape key missing: {name}")
            errors += 1

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
        _report("PASS", f"Animation clips found: {len(clip_names)}")
    else:
        _report("ERROR", "No animation clips present.")
        errors += 1

    for name in contracts.REQUIRED_ANIMATIONS:
        if name in clip_names:
            _report("PASS", f"Animation present: {name}")
        else:
            _report("ERROR", f"Required animation missing: {name}")
            errors += 1

    for name in contracts.OPTIONAL_ANIMATIONS:
        if name not in clip_names:
            _report("WARNING", f"Optional animation missing: {name}")
            warnings += 1

    materials = list(bpy.data.materials)
    if materials:
        _report("PASS", f"Materials exist: {len(materials)}")
    else:
        _report("ERROR", "No materials found.")
        errors += 1

    images = [img for img in bpy.data.images if img.size[0] > 0]
    if images:
        _report("PASS", f"Textures available: {len(images)}")
    else:
        _report("WARNING", "No packed/loaded textures (untextured materials are allowed for MVP).")
        warnings += 1

    if armature is not None:
        world_scale = armature.matrix_world.to_scale()
        if abs(world_scale.x - 1.0) > 0.01 or abs(world_scale.y - 1.0) > 0.01 or abs(world_scale.z - 1.0) > 0.01:
            _report("WARNING", "Armature world scale is not 1,1,1. Apply scale before export.")
            warnings += 1
        else:
            _report("PASS", "Armature scale is reasonable (approx 1,1,1).")

        loc = armature.matrix_world.to_translation()
        if abs(loc.x) > 0.5 or abs(loc.y) > 0.5:
            _report("WARNING", "Armature is offset from origin; presenter may sit off-camera.")
            warnings += 1
        else:
            _report("PASS", "Armature is near the world origin.")

    print("---")
    print(f"SUMMARY: errors={errors} warnings={warnings}")
    if errors:
        print("RESULT: ERROR")
        return 1
    print("RESULT: PASS" if warnings == 0 else "RESULT: WARNING")
    return 0


if __name__ == "__main__":
    sys.exit(validate())
