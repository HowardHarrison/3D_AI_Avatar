"""Import an external GLB as the Blender source presenter.blend.

Use this when adopting a licensed/base character into the pipeline. The GLB is
imported into a clean scene and saved as ``blender/source/presenter.blend``.
Existing ``presenter.blend`` is version-backed up when present (unless
``--no-backup``).

    blender --background --python blender/scripts/import_base_glb.py -- --input blender/exports/giga_chad.glb

Then inspect / validate:

    blender --background blender/source/presenter.blend --python blender/scripts/inspect_scene.py
    blender --background blender/source/presenter.blend --python blender/scripts/validate_rig.py
"""

from __future__ import annotations

import argparse
import importlib.util
import shutil
import sys
from datetime import datetime
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


def _clear_scene(bpy) -> None:
    """Remove all objects from the current scene."""
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    for collection in (
        bpy.data.meshes,
        bpy.data.armatures,
        bpy.data.actions,
        bpy.data.materials,
        bpy.data.images,
    ):
        for block in list(collection):
            if block.users == 0:
                collection.remove(block)


def _backup_existing_blend(common, report) -> Path | None:
    """Copy existing presenter.blend into versions/ before overwrite."""
    src = common.presenter_blend_path()
    if not src.is_file():
        return None
    dest_dir = common.versions_dir()
    dest_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    dest = dest_dir / f"{stamp}_pre_import_{src.name}"
    shutil.copy2(src, dest)
    report("PASS", f"Backed up existing blend: {dest}")
    return dest


def import_base_glb(argv: list[str] | None = None) -> int:
    """Import a GLB file and save it as presenter.blend; return exit code."""
    common = _load_common()
    bpy = common.require_bpy()
    emit = common.emit
    report = common.report

    parser = argparse.ArgumentParser(description="Import a base character GLB into presenter.blend")
    parser.add_argument(
        "--input",
        required=True,
        help="Path to source .glb (absolute or relative to repo root)",
    )
    parser.add_argument(
        "--no-backup",
        action="store_true",
        help="Do not backup an existing presenter.blend",
    )
    parser.add_argument(
        "--skip-inspect",
        action="store_true",
        help="Skip running inspect_scene after save",
    )
    try:
        args = parser.parse_args(_script_argv(argv))
    except SystemExit as exc:
        return exc.code if isinstance(exc.code, int) else 1

    input_path = Path(args.input)
    if not input_path.is_file():
        # Try relative to repo root
        alt = common.repo_root() / args.input
        if alt.is_file():
            input_path = alt
        else:
            report("ERROR", f"Input GLB not found: {args.input}")
            emit("RESULT", "ERROR")
            return 1

    input_path = input_path.resolve()
    suffix = input_path.suffix.lower()
    if suffix not in {".glb", ".gltf", ".fbx"}:
        report("ERROR", f"Expected .glb / .gltf / .fbx, got: {input_path}")
        emit("RESULT", "ERROR")
        return 1

    emit("FILE", str(input_path))
    report("INFO", f"Importing base character ({suffix}) ({input_path.stat().st_size} bytes)")

    out = common.presenter_blend_path()
    if out.is_file() and not args.no_backup:
        _backup_existing_blend(common, report)
    elif out.is_file() and args.no_backup:
        report("WARNING", "Overwriting presenter.blend without backup (--no-backup)")

    _clear_scene(bpy)

    # Fresh empty file state for a clean import
    bpy.ops.wm.read_homefile(use_empty=True)
    _clear_scene(bpy)

    try:
        if suffix in {".glb", ".gltf"}:
            bpy.ops.import_scene.gltf(filepath=str(input_path))
        else:
            bpy.ops.import_scene.fbx(filepath=str(input_path), automatic_bone_orientation=True)
    except Exception as exc:  # noqa: BLE001
        report("ERROR", f"Import failed: {exc}")
        emit("RESULT", "ERROR")
        return 1

    objects = list(bpy.data.objects)
    armatures = [o for o in objects if o.type == "ARMATURE"]
    meshes = [o for o in objects if o.type == "MESH"]
    report("PASS", f"Imported objects={len(objects)} armatures={len(armatures)} meshes={len(meshes)}")

    if not armatures:
        report("WARNING", "No armature found after import — gestures may not work until a rig exists.")
    if not meshes:
        report("ERROR", "No meshes found after import.")
        emit("RESULT", "ERROR")
        return 1

    for arm in armatures:
        report("INFO", f"Armature: {arm.name}|bones={len(arm.data.bones)}")
        for bone in sorted(arm.data.bones, key=lambda b: b.name)[:40]:
            emit("BONE", f"{arm.name}|{bone.name}")
        if len(arm.data.bones) > 40:
            report("INFO", f"... and {len(arm.data.bones) - 40} more bones")

    out.parent.mkdir(parents=True, exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(out))
    report("PASS", f"Saved Blender source: {out}")

    if not args.skip_inspect:
        inspect_scene = common.load_scripts_module("inspect_scene")
        report("INFO", "Running inspect_scene...")
        inspect_scene.inspect_scene()

    report(
        "INFO",
        "Next: review bone/shape-key names, build bone_rename_map.json, "
        "run apply_rename_map.py, then validate_rig / avatar:release.",
    )
    emit("RESULT", "OK")
    return 0


if __name__ == "__main__":
    sys.exit(import_base_glb())
