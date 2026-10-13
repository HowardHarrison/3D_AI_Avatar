"""Apply a JSON bone rename map toward the avatar naming contract.

Use after importing a licensed character whose bone names differ (e.g. Mixamo).

    blender --background blender/source/presenter.blend --python blender/scripts/apply_rename_map.py -- --map blender/definitions/bone_rename_map.json

Dry-run (print planned renames only):

    blender --background blender/source/presenter.blend --python blender/scripts/apply_rename_map.py -- --map blender/definitions/bone_rename_map.example.json --dry-run
"""

from __future__ import annotations

import argparse
import importlib.util
import json
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


def apply_rename_map(argv: list[str] | None = None) -> int:
    """Rename bones from a JSON map; return process exit code."""
    common = _load_common()
    bpy = common.require_bpy()
    emit = common.emit
    report = common.report

    parser = argparse.ArgumentParser(description="Apply bone rename map JSON")
    parser.add_argument("--map", required=True, help="Path to bone_rename_map.json")
    parser.add_argument("--dry-run", action="store_true", help="Print renames only.")
    parser.add_argument("--no-backup", action="store_true")
    parser.add_argument("--skip-validate", action="store_true")
    try:
        args = parser.parse_args(_script_argv(argv))
    except SystemExit as exc:
        return exc.code if isinstance(exc.code, int) else 1

    map_path = Path(args.map)
    if not map_path.is_file():
        report("ERROR", f"Map file not found: {map_path}")
        emit("RESULT", "ERROR")
        return 1

    data = json.loads(map_path.read_text(encoding="utf-8"))
    armature_name = data.get("armature") or "Armature"
    bones = data.get("bones") or {}
    if not isinstance(bones, dict) or not bones:
        report("ERROR", "Map JSON must contain a non-empty 'bones' object.")
        emit("RESULT", "ERROR")
        return 1

    arm = bpy.data.objects.get(armature_name)
    if arm is None or arm.type != "ARMATURE":
        available = ", ".join(
            sorted(o.name for o in bpy.data.objects if o.type == "ARMATURE")
        ) or "(none)"
        report("ERROR", f"Armature not found: {armature_name}")
        report("INFO", f"Available armatures: {available}")
        emit("RESULT", "ERROR")
        return 1

    emit("FILE", bpy.data.filepath or "(unsaved)")
    report("INFO", f"Armature: {arm.name}")
    report("INFO", f"Planned renames: {len(bones)}")

    # Sort so we rename into free names first when possible (targets that are also sources last)
    items = list(bones.items())
    for old, new in items:
        emit("PLAN", f"{old} -> {new}")

    if args.dry_run:
        emit("RESULT", "OK")
        return 0

    if args.no_backup:
        report("WARNING", "Skipping versioned backup (--no-backup).")
    else:
        try:
            common.save_versioned_blend(label="pre_bone_rename_map")
        except RuntimeError as exc:
            report("ERROR", str(exc))
            emit("RESULT", "ERROR")
            return 1

    bpy.context.view_layer.objects.active = arm
    bpy.ops.object.mode_set(mode="EDIT")
    try:
        for old, new in items:
            if old == new:
                continue
            edit_bone = arm.data.edit_bones.get(old)
            if edit_bone is None:
                report("WARNING", f"Source bone missing (skipped): {old}")
                continue
            if new in arm.data.edit_bones and new != old:
                report("ERROR", f"Target bone name already exists: {new}")
                bpy.ops.object.mode_set(mode="OBJECT")
                emit("RESULT", "ERROR")
                return 1
            edit_bone.name = new
            report("PASS", f"Renamed bone: {old} -> {new}")
    finally:
        if arm.mode != "OBJECT":
            bpy.ops.object.mode_set(mode="OBJECT")

    if bpy.data.filepath:
        bpy.ops.wm.save_mainfile()
        report("PASS", f"Saved: {bpy.data.filepath}")

    if not args.skip_validate:
        validate_rig = common.load_scripts_module("validate_rig")
        report("INFO", "Running validate_rig...")
        if validate_rig.validate() != 0:
            report("ERROR", "validate_rig failed after renames.")
            emit("RESULT", "ERROR")
            return 1

    emit("RESULT", "OK")
    return 0


if __name__ == "__main__":
    sys.exit(apply_rename_map())
