"""Apply narrow, safe character transforms in the open .blend.

This script does **not** remesh, re-weight, sculpt, or invent anatomy.
Supported operations only:

- list mesh / armature objects and their transforms
- set object scale
- apply location / rotation / scale
- rename an object
- rename one bone on an armature (toward the naming contract)

Default flow after a change:

1. Resolve the target object (error if missing)
2. ``save_versioned_blend`` backup
3. Apply the requested operation
4. Save the working ``.blend``
5. Run ``validate_rig`` (optional skip)
6. Export to ``blender/exports/tmp/presenter.glb`` (optional skip)

List objects:

    blender --background blender/source/presenter.blend --python blender/scripts/modify_character.py -- --list

Apply transforms:

    blender --background blender/source/presenter.blend --python blender/scripts/modify_character.py -- --object Armature --apply-transforms

Set scale:

    blender --background blender/source/presenter.blend --python blender/scripts/modify_character.py -- --object Armature --scale 1,1,1

Rename object or bone:

    blender --background blender/source/presenter.blend --python blender/scripts/modify_character.py -- --object OldName --rename PresenterBody
    blender --background blender/source/presenter.blend --python blender/scripts/modify_character.py -- --armature Armature --rename-bone mixamorig:Hips=Hips

Smoke-test (unsaved default scene):

    blender --background --python blender/scripts/modify_character.py -- --list
    blender --background --python blender/scripts/modify_character.py -- --object Cube --scale 1.1,1.1,1.1 --no-backup --skip-validate --skip-export
"""

from __future__ import annotations

import argparse
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


def _script_argv(argv: list[str] | None = None) -> list[str]:
    """Return arguments after ``--`` when launched via ``blender --python``."""
    args = list(sys.argv if argv is None else argv)
    if "--" in args:
        return args[args.index("--") + 1 :]
    return args[1:]


def _parse_vec3(text: str) -> tuple[float, float, float]:
    """Parse ``X,Y,Z`` floats."""
    parts = [p.strip() for p in text.split(",")]
    if len(parts) != 3:
        raise ValueError("Expected three comma-separated floats: X,Y,Z")
    return float(parts[0]), float(parts[1]), float(parts[2])


def _parse_bone_rename(text: str) -> tuple[str, str]:
    """Parse ``OldName=NewName`` for a single bone rename."""
    if "=" not in text:
        raise ValueError("Bone rename must be OldName=NewName")
    old, new = text.split("=", 1)
    old, new = old.strip(), new.strip()
    if not old or not new:
        raise ValueError("Bone rename must be OldName=NewName (both non-empty)")
    return old, new


def _fmt_vec(values) -> str:
    """Format a 3-vector for log lines."""
    return f"({values[0]:.4f},{values[1]:.4f},{values[2]:.4f})"


def _list_objects(bpy, emit) -> int:
    """Print mesh and armature objects with transforms; return exit code."""
    objects = [obj for obj in bpy.data.objects if obj.type in {"MESH", "ARMATURE"}]
    emit("SECTION", "objects")
    if not objects:
        emit("ERROR", "No mesh or armature objects in the file.")
        emit("RESULT", "ERROR")
        return 1

    for obj in sorted(objects, key=lambda o: o.name):
        parent = obj.parent.name if obj.parent else "-"
        emit(
            "OBJECT",
            f"{obj.name}|type={obj.type}|parent={parent}"
            f"|loc={_fmt_vec(obj.location)}"
            f"|rot={_fmt_vec(obj.rotation_euler)}"
            f"|scale={_fmt_vec(obj.scale)}",
        )
        if obj.type == "ARMATURE":
            bone_names = sorted(b.name for b in obj.data.bones)
            emit("BONE_COUNT", f"{obj.name}|bones={len(bone_names)}")
            for name in bone_names:
                emit("BONE", f"{obj.name}|{name}")

    emit("COUNT", f"objects={len(objects)}")
    emit("RESULT", "OK")
    return 0


def _require_object(bpy, name: str, report):
    """Return the object named ``name`` or report available names."""
    obj = bpy.data.objects.get(name)
    if obj is not None:
        return obj
    available = ", ".join(sorted(o.name for o in bpy.data.objects)) or "(none)"
    report("ERROR", f"Object not found: {name}")
    report("INFO", f"Available objects: {available}")
    return None


def _select_active(bpy, obj) -> None:
    """Make ``obj`` the only selected active object in the view layer."""
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj


def _apply_transforms(bpy, obj, report) -> None:
    """Apply location, rotation, and scale on ``obj``."""
    if obj.type not in {"MESH", "ARMATURE", "EMPTY", "CURVE", "FONT"}:
        raise RuntimeError(f"Apply transforms is not supported for type={obj.type}")
    _select_active(bpy, obj)
    if obj.type == "ARMATURE" and obj.mode != "OBJECT":
        bpy.ops.object.mode_set(mode="OBJECT")
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    report(
        "PASS",
        f"Applied transforms on {obj.name}: "
        f"loc={_fmt_vec(obj.location)} rot={_fmt_vec(obj.rotation_euler)} "
        f"scale={_fmt_vec(obj.scale)}",
    )


def _set_scale(obj, scale: tuple[float, float, float], report) -> None:
    """Assign object scale without applying it to mesh data."""
    before = _fmt_vec(obj.scale)
    obj.scale = scale
    report("PASS", f"Set scale on {obj.name}: {before} -> {_fmt_vec(obj.scale)}")


def _rename_object(obj, new_name: str, report) -> None:
    """Rename a Blender object (Blender may append .001 if the name is taken)."""
    old = obj.name
    obj.name = new_name
    report("PASS", f"Renamed object: {old} -> {obj.name}")


def _rename_bone(bpy, armature_obj, old_name: str, new_name: str, report) -> None:
    """Rename one bone on an armature (edit mode)."""
    if armature_obj.type != "ARMATURE":
        raise RuntimeError(f"Object is not an armature: {armature_obj.name}")

    bones = armature_obj.data.bones
    if old_name not in bones:
        available = ", ".join(sorted(b.name for b in bones)) or "(none)"
        raise RuntimeError(
            f"Bone not found on {armature_obj.name}: {old_name}. Available: {available}"
        )
    if new_name in bones and new_name != old_name:
        raise RuntimeError(f"Target bone name already exists: {new_name}")

    _select_active(bpy, armature_obj)
    bpy.ops.object.mode_set(mode="EDIT")
    try:
        edit_bone = armature_obj.data.edit_bones.get(old_name)
        if edit_bone is None:
            raise RuntimeError(f"Edit bone not found: {old_name}")
        edit_bone.name = new_name
    finally:
        bpy.ops.object.mode_set(mode="OBJECT")

    report("PASS", f"Renamed bone on {armature_obj.name}: {old_name} -> {new_name}")


def _build_parser() -> argparse.ArgumentParser:
    """Create CLI parser for safe character operations."""
    parser = argparse.ArgumentParser(
        description="Safe character transforms: scale, apply, rename (no remesh).",
    )
    parser.add_argument("--list", action="store_true", help="List mesh/armature objects and exit.")
    parser.add_argument("--object", type=str, default=None, help="Target object name.")
    parser.add_argument(
        "--armature",
        type=str,
        default=None,
        help="Armature object name (for --rename-bone).",
    )
    parser.add_argument(
        "--scale",
        type=str,
        default=None,
        help="Set object scale as X,Y,Z (requires --object).",
    )
    parser.add_argument(
        "--apply-transforms",
        action="store_true",
        help="Apply loc/rot/scale on --object.",
    )
    parser.add_argument(
        "--rename",
        type=str,
        default=None,
        help="New object name (requires --object).",
    )
    parser.add_argument(
        "--rename-bone",
        type=str,
        default=None,
        help="Rename one bone as OldName=NewName (requires --armature).",
    )
    parser.add_argument(
        "--no-backup",
        action="store_true",
        help="Skip versioned .blend backup (smoke tests only).",
    )
    parser.add_argument(
        "--skip-validate",
        action="store_true",
        help="Skip validate_rig after the edit.",
    )
    parser.add_argument(
        "--skip-export",
        action="store_true",
        help="Skip exporting to blender/exports/tmp/presenter.glb.",
    )
    return parser


def _count_ops(args: argparse.Namespace) -> int:
    """Return how many mutate operations were requested."""
    return sum(
        [
            bool(args.scale),
            bool(args.apply_transforms),
            bool(args.rename),
            bool(args.rename_bone),
        ]
    )


def modify_character(argv: list[str] | None = None) -> int:
    """List or safely modify character objects; return process exit code."""
    common = _load_common()
    bpy = common.require_bpy()
    emit = common.emit
    report = common.report

    parser = _build_parser()
    try:
        args = parser.parse_args(_script_argv(argv))
    except SystemExit as exc:
        return exc.code if isinstance(exc.code, int) else 1

    blend_path = bpy.data.filepath or "(unsaved / default startup)"
    emit("FILE", blend_path)

    if args.list:
        return _list_objects(bpy, emit)

    op_count = _count_ops(args)
    if op_count == 0:
        report(
            "ERROR",
            "Provide an operation (--scale, --apply-transforms, --rename, or --rename-bone) "
            "or use --list. Pass flags after blender's -- separator.",
        )
        emit("RESULT", "ERROR")
        return 1
    if op_count > 1:
        report("ERROR", "Run one operation per invocation (safer and easier to reverse).")
        emit("RESULT", "ERROR")
        return 1

    if args.rename_bone:
        if not args.armature:
            report("ERROR", "--rename-bone requires --armature NAME.")
            emit("RESULT", "ERROR")
            return 1
    elif not args.object:
        report("ERROR", "This operation requires --object NAME.")
        emit("RESULT", "ERROR")
        return 1

    target_name = args.armature if args.rename_bone else args.object
    assert target_name is not None
    obj = _require_object(bpy, target_name, report)
    if obj is None:
        emit("RESULT", "ERROR")
        return 1

    report(
        "INFO",
        f"Target: {obj.name}|type={obj.type}|scale={_fmt_vec(obj.scale)}",
    )

    if args.no_backup:
        report("WARNING", "Skipping versioned backup (--no-backup).")
    else:
        try:
            common.save_versioned_blend(label=f"pre_character_{obj.name}")
        except RuntimeError as exc:
            report("ERROR", str(exc))
            report("INFO", "Save the .blend first, or pass --no-backup for a disposable smoke test.")
            emit("RESULT", "ERROR")
            return 1

    try:
        if args.scale is not None:
            if args.object is None:
                raise RuntimeError("--scale requires --object")
            scale = _parse_vec3(args.scale)
            _set_scale(obj, scale, report)
        elif args.apply_transforms:
            _apply_transforms(bpy, obj, report)
        elif args.rename is not None:
            _rename_object(obj, args.rename, report)
        elif args.rename_bone is not None:
            old_name, new_name = _parse_bone_rename(args.rename_bone)
            _rename_bone(bpy, obj, old_name, new_name, report)
    except (RuntimeError, ValueError) as exc:
        report("ERROR", str(exc))
        emit("RESULT", "ERROR")
        return 1

    if bpy.data.filepath:
        bpy.ops.wm.save_mainfile()
        report("PASS", f"Saved working blend: {bpy.data.filepath}")
    else:
        report("WARNING", "Working blend is unsaved; change exists only in this Blender process.")

    if not args.skip_validate:
        validate_rig = common.load_scripts_module("validate_rig")
        report("INFO", "Running validate_rig...")
        status = validate_rig.validate()
        if status != 0:
            report(
                "ERROR",
                "validate_rig failed after character edit. "
                "Restore from blender/source/versions/ if needed. Export skipped.",
            )
            emit("RESULT", "ERROR")
            return 1
    else:
        report("WARNING", "Skipped validate_rig (--skip-validate).")

    if not args.skip_export:
        export_glb = common.load_scripts_module("export_glb")
        report("INFO", "Exporting to temp GLB...")
        status = export_glb.export()
        if status != 0:
            report("ERROR", "Temp export failed after character edit.")
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
    sys.exit(modify_character())
