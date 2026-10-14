"""Export the presenter mesh as FBX for Mixamo (or similar) auto-rigging.

Mixamo requires you to upload a character in a browser (Adobe account). This
script only prepares a clean mesh FBX from ``presenter.blend``.

    blender --background blender/source/presenter.blend --python blender/scripts/export_mesh_for_mixamo.py --

Output (default):

    blender/exports/mixamo_upload/presenter_mesh.fbx

After Mixamo:

1. Download **FBX** or **GLB** with skin + preferred animations (or T-pose only).
2. Save as ``blender/exports/giga_chad_rigged.glb`` (or .fbx).
3. Tell the agent / run import + rename + release (see docs/blender-pipeline.md).
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
    # ``python export_mesh_for_mixamo.py --output ...``
    if args and str(args[0]).endswith(".py"):
        return args[1:]
    # ``blender ... --python this.py`` with no ``--`` → no script args
    return []


def _pick_mesh(bpy):
    """Prefer a mesh named Man / Presenter*; else the largest mesh by vertex count."""
    meshes = [o for o in bpy.data.objects if o.type == "MESH"]
    if not meshes:
        return None
    for preferred in ("Man", "PresenterBody", "PresenterHead", "Body"):
        for obj in meshes:
            if obj.name == preferred:
                return obj
    return max(meshes, key=lambda o: len(o.data.vertices))


def export_mesh_for_mixamo(argv: list[str] | None = None) -> int:
    """Export a Mixamo-upload FBX from the open blend; return exit code."""
    common = _load_common()
    bpy = common.require_bpy()
    emit = common.emit
    report = common.report

    parser = argparse.ArgumentParser(description="Export presenter mesh FBX for Mixamo upload")
    parser.add_argument(
        "--output",
        default=None,
        help="Output .fbx path (default: blender/exports/mixamo_upload/presenter_mesh.fbx)",
    )
    try:
        args = parser.parse_args(_script_argv(argv))
    except SystemExit as exc:
        return exc.code if isinstance(exc.code, int) else 1

    blend = bpy.data.filepath or "(unsaved)"
    emit("FILE", blend)

    mesh_obj = _pick_mesh(bpy)
    if mesh_obj is None:
        report("ERROR", "No mesh found. Import giga_chad.glb first (import_base_glb.py).")
        emit("RESULT", "ERROR")
        return 1

    # Clear selection; export only the character mesh (no empties/cameras)
    bpy.ops.object.select_all(action="DESELECT")
    mesh_obj.select_set(True)
    bpy.context.view_layer.objects.active = mesh_obj

    # Apply transforms so Mixamo sees real-world scale
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

    out = (
        Path(args.output)
        if args.output
        else common.exports_dir() / "mixamo_upload" / "presenter_mesh.fbx"
    )
    if not out.is_absolute():
        out = (common.repo_root() / out).resolve()
    out.parent.mkdir(parents=True, exist_ok=True)

    # Mixamo-friendly FBX: mesh only, no animation, Y-up / -Z forward typical for FBX
    bpy.ops.export_scene.fbx(
        filepath=str(out),
        use_selection=True,
        object_types={"MESH"},
        apply_unit_scale=True,
        bake_space_transform=True,
        add_leaf_bones=False,
        armature_nodetype="NULL",
        bake_anim=False,
        path_mode="AUTO",
        embed_textures=True,
    )

    report("PASS", f"Wrote Mixamo upload mesh: {out}")
    report("INFO", f"Mesh exported: {mesh_obj.name}|verts={len(mesh_obj.data.vertices)}")
    report(
        "INFO",
        "Next (manual): https://www.mixamo.com → Upload → Auto-Rigger → "
        "Download FBX/GLB with skin → save as blender/exports/giga_chad_rigged.glb",
    )
    emit("RESULT", "OK")
    return 0


if __name__ == "__main__":
    sys.exit(export_mesh_for_mixamo())
