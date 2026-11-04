"""Bake textures from a high-res source mesh onto a Mixamo-rigged mesh.

Option A after Mixamo: keep the Mixamo armature + skin weights, transfer look
from the original textured FBX (e.g. Hunyuan) via Cycles selected-to-active bake.

    blender --background --python blender/scripts/bake_textures_onto_rigged.py -- ^
        --rigged ai_boy_tpose_mesh.fbx ^
        --textured ai_boy_tpose_texture.fbx

Default outputs:

    blender/exports/ai_boy_rigged_textured.glb
    blender/exports/textures/ai_boy_diffuse.png
    (plus roughness / metallic / normal when present on the source)

Does not modify presenter.blend. Next: copy/rename to giga_chad_rigged.glb and
run import_base_glb.py (see blender/exports/mixamo_upload/README.md).
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
    """Remove all objects and orphan data from the scene."""
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


def _mesh_world_height(obj) -> float:
    """Return mesh height in world units (Z extent)."""
    from mathutils import Vector

    corners = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]
    zs = [c.z for c in corners]
    return max(zs) - min(zs)


def _mesh_world_center_bottom(obj) -> tuple[float, float, float]:
    """Return world-space bottom-center of the mesh bounding box."""
    from mathutils import Vector

    corners = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]
    xs = [c.x for c in corners]
    ys = [c.y for c in corners]
    zs = [c.z for c in corners]
    return ((min(xs) + max(xs)) * 0.5, (min(ys) + max(ys)) * 0.5, min(zs))


def _largest_mesh(meshes: list):
    """Return the mesh with the most vertices."""
    return max(meshes, key=lambda o: len(o.data.vertices))


def _ensure_uv(bpy, obj) -> None:
    """Ensure the mesh has at least one UV layer (Smart UV Project if missing)."""
    if obj.data.uv_layers:
        return
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.uv.smart_project(angle_limit=66.0, island_margin=0.02)
    bpy.ops.object.mode_set(mode="OBJECT")


def _align_source_to_target(bpy, source, target) -> None:
    """Uniform-scale and translate source so feet and height match the target."""
    src_h = _mesh_world_height(source)
    tgt_h = _mesh_world_height(target)
    if src_h <= 0.0 or tgt_h <= 0.0:
        raise RuntimeError("Cannot align meshes: zero height bounding box.")

    scale = tgt_h / src_h
    source.scale = (source.scale[0] * scale, source.scale[1] * scale, source.scale[2] * scale)
    bpy.context.view_layer.update()

    src_feet = _mesh_world_center_bottom(source)
    tgt_feet = _mesh_world_center_bottom(target)
    source.location = (
        source.location[0] + (tgt_feet[0] - src_feet[0]),
        source.location[1] + (tgt_feet[1] - src_feet[1]),
        source.location[2] + (tgt_feet[2] - src_feet[2]),
    )
    bpy.context.view_layer.update()

    # Bake uses evaluated geometry; keep source transforms unapplied so parenting
    # is fine, but applying keeps matrix_world stable for ray casting.
    bpy.ops.object.select_all(action="DESELECT")
    source.select_set(True)
    bpy.context.view_layer.objects.active = source
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)


def _setup_cycles(bpy, samples: int) -> None:
    """Configure Cycles CPU bake settings suitable for headless runs."""
    scene = bpy.context.scene
    scene.render.engine = "CYCLES"
    scene.cycles.device = "CPU"
    scene.cycles.samples = samples
    scene.cycles.bake_type = "DIFFUSE"
    scene.render.bake.use_pass_direct = False
    scene.render.bake.use_pass_indirect = False
    scene.render.bake.use_pass_color = True
    scene.render.bake.margin = 16
    scene.render.bake.use_selected_to_active = True
    scene.render.bake.cage_extrusion = 0.05
    scene.render.bake.max_ray_distance = 0.25


def _make_image(bpy, name: str, size: int, *, is_data: bool = False, is_normal: bool = False):
    """Create a new bake image; return the image datablock."""
    img = bpy.data.images.new(name=name, width=size, height=size, alpha=True, float_buffer=False)
    img.colorspace_settings.name = "Non-Color" if (is_data or is_normal) else "sRGB"
    if is_normal:
        # Mid-purple default for unused normal texels
        pixels = [0.5, 0.5, 1.0, 1.0] * (size * size)
        img.pixels = pixels
    return img


def _prepare_bake_target_material(bpy, obj, image):
    """Assign a bake target material with an *unlinked* active Image Texture node.

    The image node must be active/selected for ``bpy.ops.object.bake``, but must
    not feed the shader during bake (avoids Cycles circular-dependency warnings).
    """
    mat_name = "BakeTarget"
    mat = bpy.data.materials.get(mat_name) or bpy.data.materials.new(name=mat_name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()

    out = nodes.new("ShaderNodeOutputMaterial")
    out.location = (400, 0)
    bsdf = nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.location = (100, 0)
    bsdf.inputs["Base Color"].default_value = (0.5, 0.5, 0.5, 1.0)
    links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])

    tex = nodes.new("ShaderNodeTexImage")
    tex.location = (-300, 0)
    tex.image = image
    for node in nodes:
        node.select = False
    tex.select = True
    nodes.active = tex

    obj.data.materials.clear()
    obj.data.materials.append(mat)
    return mat, tex


def _select_for_bake(bpy, source, target) -> None:
    """Select source then target (active) for selected-to-active bake."""
    bpy.ops.object.select_all(action="DESELECT")
    source.select_set(True)
    target.select_set(True)
    bpy.context.view_layer.objects.active = target


def _bake(bpy, bake_type: str, pass_filter=None) -> None:
    """Run one Cycles bake; raise on failure."""
    kwargs = {
        "type": bake_type,
        "use_selected_to_active": True,
        "cage_extrusion": 0.05,
        "max_ray_distance": 0.25,
        "margin": 16,
    }
    if pass_filter is not None:
        kwargs["pass_filter"] = pass_filter
    result = bpy.ops.object.bake(**kwargs)
    if "FINISHED" not in result:
        raise RuntimeError(f"Bake {bake_type} failed: {result}")


def _find_principled(mat):
    """Return the first Principled BSDF node on a material, or None."""
    if mat is None or not mat.use_nodes or mat.node_tree is None:
        return None
    for node in mat.node_tree.nodes:
        if node.type == "BSDF_PRINCIPLED":
            return node
    return None


def _bake_metallic_via_emit(bpy, source, target, size: int, tex_dir: Path, report):
    """Bake metallic by temporarily wiring source Metallic into Emission → EMIT bake."""
    if not source.data.materials:
        report("WARNING", "Metallic bake skipped: source has no materials")
        return None
    src_mat = source.data.materials[0]
    bsdf = _find_principled(src_mat)
    if bsdf is None:
        report("WARNING", "Metallic bake skipped: no Principled BSDF on source")
        return None

    links = src_mat.node_tree.links
    metal_in = bsdf.inputs.get("Metallic")
    emit_in = bsdf.inputs.get("Emission Color") or bsdf.inputs.get("Emission")
    if metal_in is None or emit_in is None:
        report("WARNING", "Metallic bake skipped: missing Metallic/Emission sockets")
        return None

    # Remember prior emission links / defaults
    prior_emit_links = [link.from_socket for link in emit_in.links]
    prior_emit_default = tuple(emit_in.default_value) if hasattr(emit_in, "default_value") else None
    prior_emit_strength = None
    strength_in = bsdf.inputs.get("Emission Strength")
    if strength_in is not None:
        prior_emit_strength = strength_in.default_value
        strength_in.default_value = 1.0

    for link in list(emit_in.links):
        links.remove(link)
    if metal_in.links:
        links.new(metal_in.links[0].from_socket, emit_in)
    else:
        # Constant metallic value → gray emission
        val = float(metal_in.default_value)
        emit_in.default_value = (val, val, val, 1.0)

    img = _make_image(bpy, "Bake_metallic", size, is_data=True)
    _prepare_bake_target_material(bpy, target, img)
    _select_for_bake(bpy, source, target)
    report("INFO", "Baking METALLIC via EMIT…")
    try:
        _bake(bpy, "EMIT")
        path = tex_dir / "ai_boy_metallic.png"
        _save_image(img, path)
        report("PASS", f"Wrote {path}")
        result = img
    except Exception as exc:  # noqa: BLE001
        report("WARNING", f"Metallic bake skipped: {exc}")
        result = None
    finally:
        for link in list(emit_in.links):
            links.remove(link)
        for sock in prior_emit_links:
            links.new(sock, emit_in)
        if prior_emit_default is not None and not emit_in.links:
            emit_in.default_value = prior_emit_default
        if strength_in is not None and prior_emit_strength is not None:
            strength_in.default_value = prior_emit_strength

    return result


def _save_image(img, path: Path) -> None:
    """Write an image to disk as PNG and point the datablock at that filepath."""
    path.parent.mkdir(parents=True, exist_ok=True)
    img.filepath_raw = str(path)
    img.file_format = "PNG"
    img.save()


def _wire_pbr_material(bpy, obj, maps: dict, *, use_metallic_map: bool = False) -> None:
    """Rebuild the target material from baked maps (diffuse required).

    Metallic maps from AI/Hunyuan bakes are often nearly white. In glTF that
    makes the whole character a chrome blob (\"big ball\") in viewers. Default
    is metallicFactor=0 (dielectric skin/cloth); opt in with ``use_metallic_map``.
    """
    mat = bpy.data.materials.new(name="CharacterPBR")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()

    out = nodes.new("ShaderNodeOutputMaterial")
    out.location = (500, 0)
    bsdf = nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.location = (200, 0)
    bsdf.inputs["Metallic"].default_value = 0.0
    bsdf.inputs["Roughness"].default_value = 0.55
    links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])

    y = 200
    if "diffuse" in maps:
        tex = nodes.new("ShaderNodeTexImage")
        tex.location = (-400, y)
        tex.image = maps["diffuse"]
        links.new(tex.outputs["Color"], bsdf.inputs["Base Color"])
        y -= 280
    if "roughness" in maps:
        tex = nodes.new("ShaderNodeTexImage")
        tex.location = (-400, y)
        tex.image = maps["roughness"]
        tex.image.colorspace_settings.name = "Non-Color"
        links.new(tex.outputs["Color"], bsdf.inputs["Roughness"])
        y -= 280
    if use_metallic_map and "metallic" in maps:
        tex = nodes.new("ShaderNodeTexImage")
        tex.location = (-400, y)
        tex.image = maps["metallic"]
        tex.image.colorspace_settings.name = "Non-Color"
        links.new(tex.outputs["Color"], bsdf.inputs["Metallic"])
        y -= 280
    if "normal" in maps:
        tex = nodes.new("ShaderNodeTexImage")
        tex.location = (-400, y)
        tex.image = maps["normal"]
        tex.image.colorspace_settings.name = "Non-Color"
        nrm = nodes.new("ShaderNodeNormalMap")
        nrm.location = (-100, y)
        links.new(tex.outputs["Color"], nrm.inputs["Color"])
        links.new(nrm.outputs["Normal"], bsdf.inputs["Normal"])

    obj.data.materials.clear()
    obj.data.materials.append(mat)


def _apply_armature_object_scale(bpy, armatures, report) -> None:
    """Apply Mixamo's typical 0.01 armature scale so GLB skins are meter-sized."""
    for arm in armatures:
        scale = tuple(arm.scale)
        if all(abs(s - 1.0) < 1e-5 for s in scale):
            continue
        report("INFO", f"Applying armature object scale {scale} on {arm.name}")
        bpy.ops.object.select_all(action="DESELECT")
        arm.hide_set(False)
        arm.select_set(True)
        bpy.context.view_layer.objects.active = arm
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)


def bake_textures_onto_rigged(argv: list[str] | None = None) -> int:
    """Bake source textures onto a Mixamo-rigged mesh; return process exit code."""
    common = _load_common()
    bpy = common.require_bpy()
    emit = common.emit
    report = common.report

    parser = argparse.ArgumentParser(
        description="Bake high-res textures onto a Mixamo-rigged character mesh"
    )
    parser.add_argument(
        "--rigged",
        required=True,
        help="Mixamo-rigged .fbx/.glb (mesh + armature)",
    )
    parser.add_argument(
        "--textured",
        required=True,
        help="Original textured .fbx (high-res mesh + PBR maps)",
    )
    parser.add_argument(
        "--output",
        default=None,
        help="Output .glb path (default: blender/exports/ai_boy_rigged_textured.glb)",
    )
    parser.add_argument(
        "--resolution",
        type=int,
        default=2048,
        help="Bake map resolution (default: 2048)",
    )
    parser.add_argument(
        "--samples",
        type=int,
        default=8,
        help="Cycles bake samples (default: 8)",
    )
    parser.add_argument(
        "--skip-normal",
        action="store_true",
        help="Skip normal-map bake",
    )
    parser.add_argument(
        "--skip-orm",
        action="store_true",
        help="Skip roughness/metallic bakes",
    )
    parser.add_argument(
        "--use-metallic-map",
        action="store_true",
        help="Connect baked metallic map (default: off — avoids chrome-blob glTF look)",
    )
    try:
        args = parser.parse_args(_script_argv(argv))
    except SystemExit as exc:
        return exc.code if isinstance(exc.code, int) else 1

    rigged_path = _resolve_input(common, args.rigged)
    textured_path = _resolve_input(common, args.textured)
    if rigged_path is None:
        report("ERROR", f"Rigged file not found: {args.rigged}")
        emit("RESULT", "ERROR")
        return 1
    if textured_path is None:
        report("ERROR", f"Textured file not found: {args.textured}")
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
    tex_dir = common.exports_dir() / "textures"
    tex_dir.mkdir(parents=True, exist_ok=True)

    emit("FILE", str(rigged_path))
    emit("FILE", str(textured_path))
    report("INFO", "Baking textures onto Mixamo-rigged mesh (selected-to-active)")

    bpy.ops.wm.read_homefile(use_empty=True)
    _clear_scene(bpy)
    bpy.context.scene.unit_settings.system = "METRIC"
    bpy.context.scene.unit_settings.scale_length = 1.0

    # --- Import rigged target first ---
    try:
        _import_fbx(bpy, rigged_path) if rigged_path.suffix.lower() == ".fbx" else bpy.ops.import_scene.gltf(
            filepath=str(rigged_path)
        )
    except Exception as exc:  # noqa: BLE001
        report("ERROR", f"Failed to import rigged file: {exc}")
        emit("RESULT", "ERROR")
        return 1

    target_meshes = [o for o in bpy.data.objects if o.type == "MESH"]
    armatures = [o for o in bpy.data.objects if o.type == "ARMATURE"]
    if not target_meshes:
        report("ERROR", "No mesh found in rigged file.")
        emit("RESULT", "ERROR")
        return 1
    if not armatures:
        report("WARNING", "No armature in rigged file — export will be mesh-only.")

    target = _largest_mesh(target_meshes)
    _apply_armature_object_scale(bpy, armatures, report)
    target_names = {o.name for o in bpy.data.objects}
    report(
        "INFO",
        f"Target mesh={target.name}|verts={len(target.data.vertices)}|"
        f"armatures={len(armatures)}|height={_mesh_world_height(target):.3f}",
    )
    _ensure_uv(bpy, target)

    # --- Import textured source ---
    try:
        _import_fbx(bpy, textured_path)
    except Exception as exc:  # noqa: BLE001
        report("ERROR", f"Failed to import textured file: {exc}")
        emit("RESULT", "ERROR")
        return 1

    source_meshes = [
        o for o in bpy.data.objects if o.type == "MESH" and o.name not in target_names
    ]
    if not source_meshes:
        # Name collision fallback: pick densest mesh that isn't target
        source_meshes = [o for o in bpy.data.objects if o.type == "MESH" and o != target]
    if not source_meshes:
        report("ERROR", "No source mesh found in textured file.")
        emit("RESULT", "ERROR")
        return 1

    source = _largest_mesh(source_meshes)
    report(
        "INFO",
        f"Source mesh={source.name}|verts={len(source.data.vertices)}|"
        f"images={len(bpy.data.images)}|height={_mesh_world_height(source):.3f}",
    )
    if len(bpy.data.images) == 0:
        report("ERROR", "Textured file has no images to bake from.")
        emit("RESULT", "ERROR")
        return 1

    _align_source_to_target(bpy, source, target)
    report(
        "PASS",
        f"Aligned source→target height={_mesh_world_height(source):.3f} "
        f"(target={_mesh_world_height(target):.3f})",
    )

    # Hide armatures from bake rays (still kept for export)
    for arm in armatures:
        arm.hide_render = True
        arm.hide_set(True)

    _setup_cycles(bpy, samples=int(args.samples))
    size = int(args.resolution)
    maps: dict = {}

    # Diffuse / base color
    diffuse = _make_image(bpy, "BakeDiffuse", size)
    _prepare_bake_target_material(bpy, target, diffuse)
    _select_for_bake(bpy, source, target)
    report("INFO", f"Baking DIFFUSE COLOR at {size}px…")
    try:
        _bake(bpy, "DIFFUSE", pass_filter={"COLOR"})
    except Exception as exc:  # noqa: BLE001
        report("ERROR", f"Diffuse bake failed: {exc}")
        emit("RESULT", "ERROR")
        return 1
    diffuse_path = tex_dir / "ai_boy_diffuse.png"
    _save_image(diffuse, diffuse_path)
    maps["diffuse"] = diffuse
    report("PASS", f"Wrote {diffuse_path}")

    if not args.skip_orm:
        img = _make_image(bpy, "Bake_roughness", size, is_data=True)
        _prepare_bake_target_material(bpy, target, img)
        _select_for_bake(bpy, source, target)
        report("INFO", "Baking ROUGHNESS…")
        try:
            _bake(bpy, "ROUGHNESS")
            path = tex_dir / "ai_boy_roughness.png"
            _save_image(img, path)
            maps["roughness"] = img
            report("PASS", f"Wrote {path}")
        except Exception as exc:  # noqa: BLE001
            report("WARNING", f"ROUGHNESS bake skipped: {exc}")

        # Blender has no METALNESS bake type — route source Metallic → Emission, bake EMIT
        metallic_img = _bake_metallic_via_emit(
            bpy, source, target, size, tex_dir, report
        )
        if metallic_img is not None:
            maps["metallic"] = metallic_img

    if not args.skip_normal:
        nrm = _make_image(bpy, "BakeNormal", size, is_normal=True)
        _prepare_bake_target_material(bpy, target, nrm)
        _select_for_bake(bpy, source, target)
        report("INFO", "Baking NORMAL…")
        try:
            _bake(bpy, "NORMAL")
            nrm_path = tex_dir / "ai_boy_normal.png"
            _save_image(nrm, nrm_path)
            maps["normal"] = nrm
            report("PASS", f"Wrote {nrm_path}")
        except Exception as exc:  # noqa: BLE001
            report("WARNING", f"Normal bake skipped: {exc}")

    _wire_pbr_material(
        bpy, target, maps, use_metallic_map=bool(args.use_metallic_map)
    )

    # Remove everything except the rigged character mesh + its armature(s)
    keep = {target.name, *(a.name for a in armatures)}
    bpy.ops.object.select_all(action="DESELECT")
    for obj in list(bpy.data.objects):
        if obj.name not in keep:
            obj.hide_set(False)
            obj.hide_render = False
            obj.select_set(True)
    if bpy.context.selected_objects:
        bpy.ops.object.delete(use_global=False)

    for arm in [o for o in bpy.data.objects if o.type == "ARMATURE"]:
        arm.hide_render = False
        arm.hide_set(False)

    # Pack images into the export so GLB embeds them
    for img in maps.values():
        if img.filepath:
            try:
                img.pack()
            except Exception:  # noqa: BLE001
                pass

    # Select only character assets for export (avoid leftover empties/lights)
    bpy.ops.object.select_all(action="DESELECT")
    export_objs = [o for o in bpy.data.objects if o.type in {"MESH", "ARMATURE"}]
    for obj in export_objs:
        obj.select_set(True)
    arms_now = [o for o in export_objs if o.type == "ARMATURE"]
    meshes_now = [o for o in export_objs if o.type == "MESH"]
    bpy.context.view_layer.objects.active = arms_now[0] if arms_now else (
        meshes_now[0] if meshes_now else None
    )
    report(
        "INFO",
        f"Exporting objects={len(export_objs)} meshes={len(meshes_now)} armatures={len(arms_now)}",
    )

    common.assert_export_path_allowed(out)
    bpy.ops.export_scene.gltf(
        filepath=str(out),
        export_format="GLB",
        use_selection=True,
        export_apply=False,
        export_animations=False,
        export_skins=True,
        export_morph=True,
        export_materials="EXPORT",
        export_image_format="AUTO",
        export_extras=False,
    )
    report("PASS", f"Wrote textured rigged character: {out} ({out.stat().st_size} bytes)")
    report(
        "INFO",
        "Next: copy/rename to blender/exports/giga_chad_rigged.glb then "
        "import_base_glb.py → apply_rename_map.py → avatar:release",
    )
    emit("RESULT", "OK")
    return 0


if __name__ == "__main__":
    sys.exit(bake_textures_onto_rigged())
