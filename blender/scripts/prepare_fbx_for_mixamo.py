"""Import an external character FBX, clean it, and export a Mixamo-upload mesh.

Use this for unrigged / AI-generated T-pose characters (e.g. Hunyuan) before
uploading to https://www.mixamo.com Auto-Rigger.

    blender --background --python blender/scripts/prepare_fbx_for_mixamo.py -- ^
        --input ai_boy_tpose.fbx

Default output:

    blender/exports/mixamo_upload/ai_boy_mesh.fbx

Does not modify presenter.blend. After Mixamo, download the rigged character
and follow blender/exports/mixamo_upload/README.md.
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
    """Return script flags after ``--``, or plain-python argv; ignore Blender flags."""
    args = list(sys.argv if argv is None else argv)
    if "--" in args:
        return args[args.index("--") + 1 :]
    if args and str(args[0]).endswith(".py"):
        return args[1:]
    return []


def _resolve_input(common, raw: str) -> Path | None:
    """Resolve ``--input`` against cwd or repo root."""
    path = Path(raw)
    if path.is_file():
        return path.resolve()
    alt = common.repo_root() / raw
    if alt.is_file():
        return alt.resolve()
    return None


def _clear_scene(bpy) -> None:
    """Remove all objects and orphaned data blocks from the scene."""
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


def _mesh_world_height(obj) -> float:
    """Return mesh height in world units (Z extent of bounding box corners)."""
    from mathutils import Vector

    corners = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]
    zs = [c.z for c in corners]
    return max(zs) - min(zs)


def _strip_rigging(bpy, mesh_objs: list) -> None:
    """Remove armature modifiers and vertex groups so Mixamo can auto-rig cleanly."""
    for obj in mesh_objs:
        for mod in list(obj.modifiers):
            if mod.type == "ARMATURE":
                obj.modifiers.remove(mod)
        if obj.vertex_groups:
            obj.vertex_groups.clear()


def _delete_non_meshes(bpy) -> None:
    """Delete armatures, empties, cameras, lights — keep meshes only."""
    to_delete = [o for o in bpy.data.objects if o.type != "MESH"]
    if not to_delete:
        return
    bpy.ops.object.select_all(action="DESELECT")
    for obj in to_delete:
        obj.select_set(True)
    bpy.ops.object.delete(use_global=False)


def _join_meshes(bpy, mesh_objs: list):
    """Join all meshes into one object; return the active joined mesh."""
    if len(mesh_objs) == 1:
        return mesh_objs[0]
    bpy.ops.object.select_all(action="DESELECT")
    # Prefer the largest mesh as active (keeps materials more predictably)
    primary = max(mesh_objs, key=lambda o: len(o.data.vertices))
    for obj in mesh_objs:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = primary
    bpy.ops.object.join()
    return bpy.context.view_layer.objects.active


def _place_origin_at_feet(bpy, obj) -> None:
    """Set object origin to the bottom-center of the mesh bounding box."""
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj

    from mathutils import Vector

    corners = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]
    xs = [c.x for c in corners]
    ys = [c.y for c in corners]
    zs = [c.z for c in corners]
    bottom_center = (
        (min(xs) + max(xs)) * 0.5,
        (min(ys) + max(ys)) * 0.5,
        min(zs),
    )

    # Cursor to feet, origin to cursor, then move object so feet sit on world origin
    bpy.context.scene.cursor.location = bottom_center
    bpy.ops.object.origin_set(type="ORIGIN_CURSOR")
    obj.location = (0.0, 0.0, 0.0)
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)


def _normalize_human_scale(
    bpy, obj, target_height: float = 1.75, *, force: bool = True
) -> None:
    """Uniform-scale mesh toward ``target_height`` meters (Mixamo prefers ~adult height)."""
    height = _mesh_world_height(obj)
    if height <= 0.0:
        return
    if not force and 0.8 <= height <= 3.0:
        return
    if math.isclose(height, target_height, rel_tol=0.02):
        return
    scale = target_height / height
    obj.scale = (scale, scale, scale)
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)


def _replace_with_simple_material(bpy, obj) -> None:
    """Drop heavy texture materials; Mixamo auto-rig does not need textures."""
    mat = bpy.data.materials.new(name="MixamoPreview")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    bsdf = nodes.get("Principled BSDF")
    if bsdf is not None:
        bsdf.inputs["Base Color"].default_value = (0.72, 0.72, 0.72, 1.0)
    obj.data.materials.clear()
    obj.data.materials.append(mat)


def _report_mesh_health(bpy, obj, report) -> None:
    """Log non-manifold / loose counts that often break Mixamo parsing."""
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_all(action="DESELECT")
    bpy.ops.mesh.select_non_manifold()
    import bmesh

    bm = bmesh.from_edit_mesh(obj.data)
    non_manifold = sum(1 for v in bm.verts if v.select)
    bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.object.mode_set(mode="OBJECT")
    report("INFO", f"Non-manifold vertices≈{non_manifold}")


def _harden_topology(bpy, obj) -> None:
    """Triangulate and clear non-manifold leftovers Mixamo often rejects."""
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.mesh.quads_convert_to_tris(quad_method="BEAUTY", ngon_method="BEAUTY")
    bpy.ops.mesh.delete_loose()
    bpy.ops.mesh.dissolve_degenerate(threshold=0.0001)
    # Drop remaining non-manifold scraps (common on AI meshes)
    bpy.ops.mesh.select_all(action="DESELECT")
    bpy.ops.mesh.select_non_manifold()
    bpy.ops.mesh.delete(type="VERT")
    bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.mesh.fill_holes(sides=8)
    bpy.ops.mesh.normals_make_consistent(inside=False)
    bpy.ops.object.mode_set(mode="OBJECT")


def prepare_fbx_for_mixamo(argv: list[str] | None = None) -> int:
    """Import, clean, and export a Mixamo-upload FBX; return process exit code."""
    common = _load_common()
    bpy = common.require_bpy()
    emit = common.emit
    report = common.report

    parser = argparse.ArgumentParser(
        description="Prepare an external FBX mesh for Mixamo Auto-Rigger upload"
    )
    parser.add_argument(
        "--input",
        required=True,
        help="Source .fbx path (absolute or relative to repo root)",
    )
    parser.add_argument(
        "--output",
        default=None,
        help="Output .fbx path (default: blender/exports/mixamo_upload/<stem>_mesh.fbx)",
    )
    parser.add_argument(
        "--target-height",
        type=float,
        default=1.75,
        help="Force character height in meters for Mixamo (default: 1.75)",
    )
    parser.add_argument(
        "--no-force-height",
        action="store_true",
        help="Only rescale when height is outside 0.8–3.0 m",
    )
    parser.add_argument(
        "--merge-distance",
        type=float,
        default=0.0001,
        help="Merge-by-distance threshold in meters (default: 0.0001)",
    )
    parser.add_argument(
        "--max-faces",
        type=int,
        default=25_000,
        help="Decimate if face count exceeds this (default: 25000; Mixamo is unreliable above ~40k).",
    )
    parser.add_argument(
        "--embed-textures",
        action="store_true",
        help="Embed textures in FBX (default: off — large textures often make Mixamo fail)",
    )
    parser.add_argument(
        "--also-obj",
        action="store_true",
        default=True,
        help="Also write a texture-free .obj next to the FBX (default: on)",
    )
    parser.add_argument(
        "--no-obj",
        action="store_true",
        help="Skip writing the companion .obj",
    )
    try:
        args = parser.parse_args(_script_argv(argv))
    except SystemExit as exc:
        return exc.code if isinstance(exc.code, int) else 1

    input_path = _resolve_input(common, args.input)
    if input_path is None:
        report("ERROR", f"Input FBX not found: {args.input}")
        emit("RESULT", "ERROR")
        return 1
    if input_path.suffix.lower() != ".fbx":
        report("ERROR", f"Expected .fbx, got: {input_path}")
        emit("RESULT", "ERROR")
        return 1

    out = (
        Path(args.output)
        if args.output
        else common.exports_dir() / "mixamo_upload" / f"{input_path.stem}_mesh.fbx"
    )
    if not out.is_absolute():
        out = (common.repo_root() / out).resolve()
    out.parent.mkdir(parents=True, exist_ok=True)

    emit("FILE", str(input_path))
    report("INFO", f"Preparing Mixamo upload from {input_path.name} ({input_path.stat().st_size} bytes)")

    bpy.ops.wm.read_homefile(use_empty=True)
    _clear_scene(bpy)

    # Metric units help FBX exporters produce Mixamo-friendly scale
    bpy.context.scene.unit_settings.system = "METRIC"
    bpy.context.scene.unit_settings.scale_length = 1.0

    try:
        bpy.ops.import_scene.fbx(
            filepath=str(input_path),
            automatic_bone_orientation=True,
            use_image_search=True,
        )
    except Exception as exc:  # noqa: BLE001
        report("ERROR", f"FBX import failed: {exc}")
        emit("RESULT", "ERROR")
        return 1

    mesh_objs = [o for o in bpy.data.objects if o.type == "MESH"]
    armature_objs = [o for o in bpy.data.objects if o.type == "ARMATURE"]
    report(
        "INFO",
        f"Imported meshes={len(mesh_objs)} armatures={len(armature_objs)} "
        f"objects={len(bpy.data.objects)}",
    )
    if not mesh_objs:
        report("ERROR", "No meshes found after FBX import.")
        emit("RESULT", "ERROR")
        return 1

    for obj in mesh_objs:
        report("INFO", f"Mesh: {obj.name}|verts={len(obj.data.vertices)}")

    _strip_rigging(bpy, mesh_objs)
    _delete_non_meshes(bpy)
    mesh_objs = [o for o in bpy.data.objects if o.type == "MESH"]
    if not mesh_objs:
        report("ERROR", "All meshes disappeared after stripping non-mesh objects.")
        emit("RESULT", "ERROR")
        return 1

    body = _join_meshes(bpy, mesh_objs)
    body.name = "Character"

    # Apply any leftover object transforms before geometry cleanup
    bpy.ops.object.select_all(action="DESELECT")
    body.select_set(True)
    bpy.context.view_layer.objects.active = body
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

    # Optional override of merge distance via re-run of cleanup with CLI value
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.mesh.remove_doubles(threshold=float(args.merge_distance))
    bpy.ops.mesh.delete_loose()
    bpy.ops.mesh.normals_make_consistent(inside=False)
    bpy.ops.object.mode_set(mode="OBJECT")

    face_count = len(body.data.polygons)
    max_faces = int(args.max_faces)
    if max_faces > 0 and face_count > max_faces:
        ratio = max_faces / float(face_count)
        report(
            "INFO",
            f"Decimating for Mixamo: faces={face_count} → target≈{max_faces} (ratio={ratio:.4f})",
        )
        dec = body.modifiers.new(name="MixamoDecimate", type="DECIMATE")
        dec.ratio = ratio
        bpy.ops.object.select_all(action="DESELECT")
        body.select_set(True)
        bpy.context.view_layer.objects.active = body
        bpy.ops.object.modifier_apply(modifier=dec.name)
        report(
            "PASS",
            f"After decimate: verts={len(body.data.vertices)}|faces={len(body.data.polygons)}",
        )
    elif face_count > 40_000:
        report(
            "WARNING",
            f"Face count {face_count} is high for Mixamo; consider lowering --max-faces.",
        )

    # Scale first, then feet origin, then harden topology for the final mesh
    _normalize_human_scale(
        bpy,
        body,
        target_height=float(args.target_height),
        force=not bool(args.no_force_height),
    )
    _place_origin_at_feet(bpy, body)
    _harden_topology(bpy, body)
    _replace_with_simple_material(bpy, body)
    _report_mesh_health(bpy, body, report)

    height = _mesh_world_height(body)
    report(
        "PASS",
        f"Clean mesh ready: name={body.name}|verts={len(body.data.vertices)}"
        f"|faces={len(body.data.polygons)}|height_m={height:.3f}",
    )
    if abs(height - float(args.target_height)) > 0.05:
        report(
            "WARNING",
            f"Height {height:.3f}m differs from target {args.target_height:.2f}m.",
        )

    bpy.ops.object.select_all(action="DESELECT")
    body.select_set(True)
    bpy.context.view_layer.objects.active = body

    # Texture-free FBX keeps uploads small (~1–5 MB) — Mixamo often times out on 20–30 MB files
    embed = bool(args.embed_textures)
    bpy.ops.export_scene.fbx(
        filepath=str(out),
        use_selection=True,
        object_types={"MESH"},
        apply_unit_scale=True,
        bake_space_transform=True,
        add_leaf_bones=False,
        armature_nodetype="NULL",
        bake_anim=False,
        path_mode="COPY" if embed else "AUTO",
        embed_textures=embed,
        axis_forward="-Z",
        axis_up="Y",
        use_mesh_modifiers=True,
        mesh_smooth_type="FACE",
    )
    report("PASS", f"Wrote Mixamo upload mesh: {out} ({out.stat().st_size} bytes)")

    write_obj = bool(args.also_obj) and not bool(args.no_obj)
    if write_obj:
        obj_out = out.with_suffix(".obj")
        bpy.ops.wm.obj_export(
            filepath=str(obj_out),
            export_selected_objects=True,
            export_materials=False,
            export_uv=True,
            export_normals=True,
            forward_axis="NEGATIVE_Z",
            up_axis="Y",
        )
        report("PASS", f"Wrote Mixamo fallback OBJ: {obj_out} ({obj_out.stat().st_size} bytes)")
        report("INFO", "If FBX still fails, upload the .obj instead (gray is OK for Auto-Rigger).")

    report(
        "INFO",
        "Next (manual): https://www.mixamo.com → Upload Character → "
        f"{out.name} (or .obj) → Auto-Rigger → Download FBX/GLB With Skin → "
        "save as blender/exports/giga_chad_rigged.fbx (or .glb)",
    )
    emit("RESULT", "OK")
    return 0


if __name__ == "__main__":
    sys.exit(prepare_fbx_for_mixamo())
