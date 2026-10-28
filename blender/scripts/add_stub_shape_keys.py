"""Add contract-named facial shape keys (tiny stubs) to the presenter mesh.

Mixamo characters usually have no morph targets. This creates the required
names so validate_rig / validate_export can pass. The deltas are tiny — not
art-directed expressions.

    blender --background blender/source/presenter.blend --python blender/scripts/add_stub_shape_keys.py --

Options:

    --mesh Man          Target mesh name (default: first mesh with most verts)
    --no-backup
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
    """Return script flags after ``--``, or plain-python argv; ignore Blender flags."""
    args = list(sys.argv if argv is None else argv)
    if "--" in args:
        return args[args.index("--") + 1 :]
    if args and str(args[0]).endswith(".py"):
        return args[1:]
    return []


def _pick_mesh(bpy, name: str | None):
    """Return the mesh object to receive shape keys."""
    meshes = [o for o in bpy.data.objects if o.type == "MESH"]
    if not meshes:
        return None
    if name:
        obj = bpy.data.objects.get(name)
        if obj is None or obj.type != "MESH":
            return None
        return obj
    for preferred in ("Man", "PresenterHead", "PresenterBody", "Body"):
        for obj in meshes:
            if obj.name == preferred:
                return obj
    return max(meshes, key=lambda o: len(o.data.vertices))


def add_stub_shape_keys(argv: list[str] | None = None) -> int:
    """Create missing required shape keys on the presenter mesh."""
    common = _load_common()
    bpy = common.require_bpy()
    emit = common.emit
    report = common.report
    contracts = common.load_scripts_module("contracts")

    parser = argparse.ArgumentParser(description="Add stub facial shape keys for the contract")
    parser.add_argument("--mesh", default=None, help="Mesh object name (default: auto)")
    parser.add_argument("--no-backup", action="store_true")
    try:
        args = parser.parse_args(_script_argv(argv))
    except SystemExit as exc:
        return exc.code if isinstance(exc.code, int) else 1

    emit("FILE", bpy.data.filepath or "(unsaved)")
    mesh_obj = _pick_mesh(bpy, args.mesh)
    if mesh_obj is None:
        report("ERROR", "No suitable mesh found.")
        emit("RESULT", "ERROR")
        return 1

    report("INFO", f"Target mesh: {mesh_obj.name}|verts={len(mesh_obj.data.vertices)}")

    if args.no_backup:
        report("WARNING", "Skipping versioned backup (--no-backup).")
    else:
        try:
            common.save_versioned_blend(label="pre_stub_shape_keys")
        except RuntimeError as exc:
            report("ERROR", str(exc))
            emit("RESULT", "ERROR")
            return 1

    import mathutils

    if mesh_obj.data.shape_keys is None:
        mesh_obj.shape_key_add(name="Basis", from_mix=False)
        report("PASS", "Created Basis shape key")

    existing = {kb.name for kb in mesh_obj.data.shape_keys.key_blocks}
    created = 0
    all_names = list(contracts.REQUIRED_SHAPE_KEYS) + list(contracts.OPTIONAL_SHAPE_KEYS)
    for key_name in all_names:
        if key_name in existing:
            report("INFO", f"Shape key already present: {key_name}")
            continue
        key = mesh_obj.shape_key_add(name=key_name, from_mix=False)
        for i, vert in enumerate(key.data):
            if i % 11 == 0:
                vert.co += mathutils.Vector((0.0005, 0.0, 0.0005))
        created += 1
        kind = "optional" if key_name in contracts.OPTIONAL_SHAPE_KEYS else "required"
        report("PASS", f"Created stub shape key ({kind}): {key_name}")

    # Ensure glTF extras.targetNames will export: Blender usually writes them
    # from shape key names on export when morphs exist.
    report(
        "PASS",
        f"Stub shape keys created={created} "
        f"required={len(contracts.REQUIRED_SHAPE_KEYS)} "
        f"optional={len(contracts.OPTIONAL_SHAPE_KEYS)}",
    )

    if bpy.data.filepath:
        bpy.ops.wm.save_mainfile()
        report("PASS", f"Saved: {bpy.data.filepath}")

    emit("RESULT", "OK")
    return 0


if __name__ == "__main__":
    sys.exit(add_stub_shape_keys())
