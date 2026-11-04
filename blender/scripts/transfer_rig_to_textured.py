"""Bind a Mixamo armature to the original textured mesh (exact materials/UVs).

Keeps Hunyuan textures/UVs. Aligns the textured mesh to the Mixamo body, then
binds with Blender automatic weights (avoids broken weight-transfer + export
binds that pull hands toward an offset rig).

    blender --background --python blender/scripts/transfer_rig_to_textured.py -- ^
        --rigged ai_boy_tpose_mesh.fbx ^
        --textured ai_boy_tpose_texture.fbx

Outputs (under blender/exports/):

    ai_boy_rigged_textured.blend   ← open this in Blender
    ai_boy_rigged_textured.fbx
    ai_boy_rigged_textured.glb
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


def _resolve_input(common, raw: str) -> Path | None:
    """Resolve a path against cwd or repo root."""
    path = Path(raw)
    if path.is_file():
        return path.resolve()
    alt = common.repo_root() / raw
    if alt.is_file():
        return alt.resolve()
    return None


def _clear_scene(bpy) -> None:
    """Remove all objects from the scene."""
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


def _import_fbx(bpy, path: Path) -> None:
    """Import an FBX with image search enabled."""
    bpy.ops.import_scene.fbx(
        filepath=str(path),
        automatic_bone_orientation=True,
        use_image_search=True,
    )


def _largest_mesh(meshes: list):
    """Return the mesh with the most vertices."""
    return max(meshes, key=lambda o: len(o.data.vertices))


def _apply_all_transforms(bpy, obj) -> None:
    """Apply location, rotation, and scale on ``obj``."""
    bpy.ops.object.select_all(action="DESELECT")
    obj.hide_set(False)
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    if obj.type == "MESH":
        obj.data.update()


def _world_bbox(obj):
    """Return (min_corner, max_corner, center, size) in world space from live verts."""
    from mathutils import Vector

    mat = obj.matrix_world
    xs, ys, zs = [], [], []
    for v in obj.data.vertices:
        p = mat @ v.co
        xs.append(p.x)
        ys.append(p.y)
        zs.append(p.z)
    mn = Vector((min(xs), min(ys), min(zs)))
    mx = Vector((max(xs), max(ys), max(zs)))
    return mn, mx, (mn + mx) * 0.5, (mx - mn)


def _hip_world(armature_obj):
    """Return world position of the Hips bone head."""
    from mathutils import Vector

    hip = next((b for b in armature_obj.data.bones if "Hips" in b.name), None)
    if hip is None:
        return None
    pb = armature_obj.pose.bones.get(hip.name)
    if pb is not None:
        return armature_obj.matrix_world @ pb.matrix @ Vector((0.0, 0.0, 0.0))
    return armature_obj.matrix_world @ hip.head_local


def _report_overlap(mesh_obj, armature_obj, report, label: str) -> float:
    """Log hip→mesh-center distance; return distance in meters."""
    _, _, center, size = _world_bbox(mesh_obj)
    hip = _hip_world(armature_obj)
    if hip is None:
        report("WARNING", f"{label}: no Hips bone")
        return 999.0
    dist = (hip - center).length
    report(
        "INFO",
        f"{label}: hip→center={dist:.3f}m size=({size.x:.2f},{size.y:.2f},{size.z:.2f}) "
        f"hip={tuple(round(v, 3) for v in hip)} center={tuple(round(v, 3) for v in center)}",
    )
    return dist


def _align_to_reference(bpy, source, reference, report) -> None:
    """Scale+move ``source`` so its world AABB matches ``reference`` (uniform scale by height)."""
    s_mn, s_mx, s_c, s_sz = _world_bbox(source)
    r_mn, r_mx, r_c, r_sz = _world_bbox(reference)
    # Prefer the largest axis as height proxy (Mixamo often Y-up after import)
    s_h = max(s_sz.x, s_sz.y, s_sz.z)
    r_h = max(r_sz.x, r_sz.y, r_sz.z)
    if s_h <= 1e-8 or r_h <= 1e-8:
        raise RuntimeError("Cannot align: zero-sized mesh bounds")

    factor = r_h / s_h
    source.scale = (source.scale[0] * factor, source.scale[1] * factor, source.scale[2] * factor)
    bpy.context.view_layer.update()

    # Recompute after scale; match centers
    _, _, s_c, _ = _world_bbox(source)
    source.location = (
        source.location[0] + (r_c.x - s_c.x),
        source.location[1] + (r_c.y - s_c.y),
        source.location[2] + (r_c.z - s_c.z),
    )
    bpy.context.view_layer.update()
    _apply_all_transforms(bpy, source)

    _, _, s_c2, s_sz2 = _world_bbox(source)
    _, _, r_c2, r_sz2 = _world_bbox(reference)
    report(
        "PASS",
        f"Aligned centers src={tuple(round(v, 3) for v in s_c2)} "
        f"ref={tuple(round(v, 3) for v in r_c2)} "
        f"height≈{max(s_sz2):.3f}/{max(r_sz2):.3f}",
    )


def _decimate_preserve_uv(bpy, obj, max_faces: int, report) -> None:
    """Decimate while keeping UVs."""
    faces = len(obj.data.polygons)
    if max_faces <= 0 or faces <= max_faces:
        return
    ratio = max_faces / float(faces)
    report("INFO", f"Decimating faces={faces} → ≈{max_faces} (UVs kept)")
    mod = obj.modifiers.new(name="WebDecimate", type="DECIMATE")
    mod.ratio = ratio
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.modifier_apply(modifier=mod.name)
    report("PASS", f"After decimate verts={len(obj.data.vertices)} faces={len(obj.data.polygons)}")


def _resize_images(bpy, max_size: int, report) -> None:
    """Downscale images for smaller exports."""
    if max_size <= 0:
        return
    for img in list(bpy.data.images):
        w, h = img.size
        if w == 0 or h == 0 or max(w, h) <= max_size:
            continue
        scale = max_size / float(max(w, h))
        nw, nh = max(1, int(w * scale)), max(1, int(h * scale))
        report("INFO", f"Resize {img.name}: {w}x{h} → {nw}x{nh}")
        img.scale(nw, nh)


def _force_dielectric(bpy, obj, report) -> None:
    """Force Metallic=0 to avoid chrome look."""
    for slot in obj.material_slots:
        mat = slot.material
        if mat is None or not mat.use_nodes or mat.node_tree is None:
            continue
        for node in mat.node_tree.nodes:
            if node.type != "BSDF_PRINCIPLED":
                continue
            metal = node.inputs.get("Metallic")
            if metal is None:
                continue
            for link in list(metal.links):
                mat.node_tree.links.remove(link)
            metal.default_value = 0.0
            report("INFO", f"Metallic=0 on {mat.name}")


def _bind_automatic_weights(bpy, mesh_obj, armature_obj, report) -> None:
    """Parent mesh to armature with automatic weights (bones must overlap mesh)."""
    # Clear old armature mods / groups
    for mod in list(mesh_obj.modifiers):
        if mod.type == "ARMATURE":
            mesh_obj.modifiers.remove(mod)
    mesh_obj.vertex_groups.clear()
    if mesh_obj.parent is not None:
        bpy.ops.object.select_all(action="DESELECT")
        mesh_obj.select_set(True)
        bpy.context.view_layer.objects.active = mesh_obj
        bpy.ops.object.parent_clear(type="CLEAR_KEEP_TRANSFORM")

    bpy.ops.object.select_all(action="DESELECT")
    mesh_obj.select_set(True)
    armature_obj.select_set(True)
    bpy.context.view_layer.objects.active = armature_obj
    bpy.ops.object.parent_set(type="ARMATURE_AUTO")
    report(
        "PASS",
        f"Automatic weights: groups={len(mesh_obj.vertex_groups)} parent={mesh_obj.parent}",
    )


def transfer_rig_to_textured(argv: list[str] | None = None) -> int:
    """Align textured mesh to Mixamo armature and bind; return exit code."""
    common = _load_common()
    bpy = common.require_bpy()
    emit = common.emit
    report = common.report

    parser = argparse.ArgumentParser(
        description="Bind Mixamo armature to original textured mesh (automatic weights)"
    )
    parser.add_argument("--rigged", required=True, help="Mixamo-rigged .fbx")
    parser.add_argument("--textured", required=True, help="Original textured .fbx")
    parser.add_argument(
        "--output",
        default=None,
        help="Output .glb path (also writes .blend/.fbx beside it)",
    )
    parser.add_argument("--max-faces", type=int, default=60_000)
    parser.add_argument("--max-texture-size", type=int, default=2048)
    try:
        args = parser.parse_args(_script_argv(argv))
    except SystemExit as exc:
        return exc.code if isinstance(exc.code, int) else 1

    rigged_path = _resolve_input(common, args.rigged)
    textured_path = _resolve_input(common, args.textured)
    if rigged_path is None or textured_path is None:
        report("ERROR", "Input FBX not found")
        emit("RESULT", "ERROR")
        return 1

    out = (
        Path(args.output)
        if args.output
        else common.exports_dir() / "ai_boy_rigged_textured.glb"
    )
    if not out.is_absolute():
        out = (common.repo_root() / out).resolve()
    out.parent.mkdir(parents=True, exist_ok=True)

    emit("FILE", str(rigged_path))
    emit("FILE", str(textured_path))
    report("INFO", "Align textured mesh → Mixamo armature → automatic weights")

    bpy.ops.wm.read_homefile(use_empty=True)
    _clear_scene(bpy)
    bpy.context.scene.unit_settings.system = "METRIC"
    bpy.context.scene.unit_settings.scale_length = 1.0

    # --- Mixamo ---
    try:
        _import_fbx(bpy, rigged_path)
    except Exception as exc:  # noqa: BLE001
        report("ERROR", f"Rigged import failed: {exc}")
        emit("RESULT", "ERROR")
        return 1

    mixamo = _largest_mesh([o for o in bpy.data.objects if o.type == "MESH"])
    armature = next(o for o in bpy.data.objects if o.type == "ARMATURE")
    # Keep Mixamo armature object scale (0.01) + 90° X as imported.
    # Applying those object transforms in Blender 5.x moves bone heads ~1.3 m
    # behind the mesh and is what stretched the hands.
    report(
        "INFO",
        f"Keeping Mixamo armature object xforms scale={tuple(round(s, 5) for s in armature.scale)} "
        f"rot={tuple(round(r, 4) for r in armature.rotation_euler)}",
    )
    mixamo.name = "MixamoDonor"
    if mixamo.data:
        mixamo.data.name = "MixamoDonorMesh"
    before = {o.name for o in bpy.data.objects}
    donor_hip_dist = _report_overlap(mixamo, armature, report, "Mixamo donor")
    if donor_hip_dist > 0.35:
        report(
            "ERROR",
            f"Mixamo donor already misaligned (hip→center={donor_hip_dist:.3f}m). Abort.",
        )
        emit("RESULT", "ERROR")
        return 1

    # --- Textured ---
    try:
        _import_fbx(bpy, textured_path)
    except Exception as exc:  # noqa: BLE001
        report("ERROR", f"Textured import failed: {exc}")
        emit("RESULT", "ERROR")
        return 1

    textured = _largest_mesh(
        [o for o in bpy.data.objects if o.type == "MESH" and o.name not in before]
    )
    if textured.parent is not None:
        bpy.ops.object.select_all(action="DESELECT")
        textured.select_set(True)
        bpy.context.view_layer.objects.active = textured
        bpy.ops.object.parent_clear(type="CLEAR_KEEP_TRANSFORM")
    _apply_all_transforms(bpy, textured)

    _align_to_reference(bpy, textured, mixamo, report)
    _decimate_preserve_uv(bpy, textured, int(args.max_faces), report)
    # Re-align after decimate (origin can shift slightly)
    _align_to_reference(bpy, textured, mixamo, report)
    _resize_images(bpy, int(args.max_texture_size), report)
    _force_dielectric(bpy, textured, report)

    # Confirm mesh↔mesh + mesh↔hip overlap BEFORE removing donor / binding
    _, _, tex_c, _ = _world_bbox(textured)
    _, _, mix_c, _ = _world_bbox(mixamo)
    mesh_mesh_dist = (tex_c - mix_c).length
    report("INFO", f"Pre-bind mesh↔donor center dist={mesh_mesh_dist:.4f}m")
    if mesh_mesh_dist > 0.05:
        report("ERROR", f"Textured mesh not aligned to donor (dist={mesh_mesh_dist:.3f}m). Abort.")
        emit("RESULT", "ERROR")
        return 1
    dist = _report_overlap(textured, armature, report, "Pre-bind textured")
    if dist > 0.35:
        report("ERROR", f"Textured mesh not overlapping armature (dist={dist:.3f}m). Abort.")
        emit("RESULT", "ERROR")
        return 1

    # Remove donor mesh so automatic weights use only the textured body
    bpy.ops.object.select_all(action="DESELECT")
    mixamo.select_set(True)
    bpy.ops.object.delete(use_global=False)
    for mesh in list(bpy.data.meshes):
        if mesh.users == 0:
            bpy.data.meshes.remove(mesh)

    textured.name = "Character"
    if textured.data:
        textured.data.name = "CharacterMesh"

    _bind_automatic_weights(bpy, textured, armature, report)
    dist2 = _report_overlap(textured, armature, report, "Post-bind")
    if dist2 > 0.35:
        report("ERROR", f"Bind left mesh offset from armature (dist={dist2:.3f}m).")
        emit("RESULT", "ERROR")
        return 1
    report("PASS", "Mesh and armature overlap; automatic weights applied")

    # Pack textures
    for img in bpy.data.images:
        try:
            if img.filepath or img.packed_file:
                img.pack()
        except Exception:  # noqa: BLE001
            pass

    # Save .blend first (authoritative for Blender viewing)
    blend_out = out.with_suffix(".blend")
    bpy.ops.wm.save_as_mainfile(filepath=str(blend_out))
    report("PASS", f"Wrote {blend_out}")

    bpy.ops.object.select_all(action="DESELECT")
    textured.select_set(True)
    armature.select_set(True)
    bpy.context.view_layer.objects.active = armature

    fbx_out = out.with_suffix(".fbx")
    common.assert_export_path_allowed(fbx_out)
    bpy.ops.export_scene.fbx(
        filepath=str(fbx_out),
        use_selection=True,
        object_types={"ARMATURE", "MESH"},
        apply_unit_scale=True,
        bake_space_transform=False,
        add_leaf_bones=False,
        bake_anim=False,
        path_mode="COPY",
        embed_textures=True,
        use_armature_deform_only=True,
    )
    report("PASS", f"Wrote {fbx_out} ({fbx_out.stat().st_size} bytes)")

    common.assert_export_path_allowed(out)
    bpy.ops.export_scene.gltf(
        filepath=str(out),
        export_format="GLB",
        use_selection=True,
        export_animations=False,
        export_skins=True,
        export_materials="EXPORT",
        export_rest_position_armature=True,
    )
    report("PASS", f"Wrote {out} ({out.stat().st_size} bytes)")
    report(
        "INFO",
        "In Blender: File → Open ai_boy_rigged_textured.blend "
        "(or Import the .fbx). Then Z → Material Preview.",
    )
    emit("RESULT", "OK")
    return 0


if __name__ == "__main__":
    sys.exit(transfer_rig_to_textured())
