"""Rebuild contract facial shape keys with visible head-region deformations.

Mixamo meshes have no authored morphs. Tiny stubs from ``add_stub_shape_keys``
are invisible. This script estimates head vertices from the Head bone and
applies larger, region-based deltas so ``FacialController`` expressions read
in the browser. Quality is approximate — not production face rigging.

    blender --background blender/source/presenter.blend --python blender/scripts/improve_facial_shape_keys.py --
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


def _find_armature(bpy):
    """Return the first armature object."""
    for obj in bpy.data.objects:
        if obj.type == "ARMATURE":
            return obj
    return None


def _pick_mesh(bpy):
    """Return the main character mesh."""
    meshes = [o for o in bpy.data.objects if o.type == "MESH"]
    if not meshes:
        return None
    for preferred in ("Man", "PresenterHead", "Body"):
        for obj in meshes:
            if obj.name == preferred:
                return obj
    return max(meshes, key=lambda o: len(o.data.vertices))


def _head_vertex_data(bpy, arm, mesh_obj):
    """Return head vertex indices and per-vertex local coords in head space.

    Uses distance to the Head bone center; radius scales with bone length.
    """
    import mathutils

    bone = arm.data.bones.get("Head")
    if bone is None:
        raise RuntimeError("Head bone not found — rename Mixamo bones first.")

    head_local = (bone.head_local + bone.tail_local) * 0.5
    head_world = arm.matrix_world @ head_local
    bone_len = (bone.tail_local - bone.head_local).length
    # Keep the region on the skull/face — too large a radius pulls in torso verts
    # and dilutes morphs (seen on Mixamo busts).
    radius = max(0.08, bone_len * 1.35)

    # Head-aligned basis from armature world rotation
    rot = arm.matrix_world.to_quaternion().to_matrix().to_4x4()
    head_matrix = mathutils.Matrix.Translation(head_world) @ rot
    head_inv = head_matrix.inverted()

    indices: list[int] = []
    locals_: list = []
    mesh_world = mesh_obj.matrix_world

    for i, vert in enumerate(mesh_obj.data.vertices):
        world = mesh_world @ vert.co
        if (world - head_world).length <= radius:
            local = head_inv @ world
            indices.append(i)
            locals_.append(local)

    if len(indices) < 20:
        raise RuntimeError(
            f"Too few head vertices found ({len(indices)}). "
            "Check Head bone placement / character scale."
        )
    return indices, locals_


def _reset_shape_keys(mesh_obj, contracts) -> None:
    """Clear shape keys and recreate Basis + required/optional empty keys."""
    if mesh_obj.data.shape_keys is not None:
        mesh_obj.shape_key_clear()
    mesh_obj.shape_key_add(name="Basis", from_mix=False)
    for name in contracts.REQUIRED_SHAPE_KEYS:
        mesh_obj.shape_key_add(name=name, from_mix=False)
    for name in contracts.OPTIONAL_SHAPE_KEYS:
        mesh_obj.shape_key_add(name=name, from_mix=False)


def _apply_deltas(key_block, indices, offsets) -> None:
    """Write world-space-ish offsets into a shape key (mesh local coords)."""
    for idx, offset in zip(indices, offsets):
        key_block.data[idx].co = key_block.data[idx].co + offset


def improve_facial_shape_keys(argv: list[str] | None = None) -> int:
    """Rebuild visible stub facial morphs; return exit code."""
    try:
        return _improve_impl(argv)
    except Exception as exc:  # noqa: BLE001
        print(f"ERROR: {exc}")
        print("RESULT: ERROR")
        return 1


def _improve_impl(argv: list[str] | None = None) -> int:
    """Implementation body for improve_facial_shape_keys."""
    common = _load_common()
    bpy = common.require_bpy()
    emit = common.emit
    report = common.report
    contracts = common.load_scripts_module("contracts")

    parser = argparse.ArgumentParser(description="Improve facial shape keys for Mixamo meshes")
    parser.add_argument("--no-backup", action="store_true")
    try:
        args = parser.parse_args(_script_argv(argv))
    except SystemExit as exc:
        return exc.code if isinstance(exc.code, int) else 1

    emit("FILE", bpy.data.filepath or "(unsaved)")
    arm = _find_armature(bpy)
    mesh_obj = _pick_mesh(bpy)
    if arm is None or mesh_obj is None:
        report("ERROR", "Need armature + mesh in the file.")
        emit("RESULT", "ERROR")
        return 1

    if args.no_backup:
        report("WARNING", "Skipping versioned backup (--no-backup).")
    else:
        try:
            common.save_versioned_blend(label="pre_improve_face")
        except RuntimeError as exc:
            report("ERROR", str(exc))
            emit("RESULT", "ERROR")
            return 1

    import mathutils

    try:
        indices, locals_ = _head_vertex_data(bpy, arm, mesh_obj)
    except RuntimeError as exc:
        report("ERROR", str(exc))
        emit("RESULT", "ERROR")
        return 1

    report("PASS", f"Head vertices: {len(indices)} on mesh {mesh_obj.name}")

    ys = [v.y for v in locals_]
    zs = [v.z for v in locals_]
    xs = [v.x for v in locals_]
    y_min, y_max = min(ys), max(ys)
    z_min, z_max = min(zs), max(zs)
    y_span = max(1e-4, y_max - y_min)
    z_span = max(1e-4, z_max - z_min)
    # Scale deltas to head size so Mixamo exports stay readable (prior export
    # had ~0.1mm displacements — invisible on a bust shot).
    head_size = max(
        max(xs) - min(xs),
        y_span,
        z_span,
        1e-3,
    )
    # Keep stylized but mild — oversized deltas on a clay Mixamo head look shredded.
    s = head_size * 0.025
    report("INFO", f"Head extent≈{head_size:.4f}; morph unit scale s={s:.4f}")

    bpy.context.view_layer.objects.active = mesh_obj
    _reset_shape_keys(mesh_obj, contracts)

    # Mesh-local offset helpers: Mixamo Y-up. Vertex normals are used when present
    # (Blender 5 no longer exposes Mesh.calc_normals()).

    def key(name: str):
        return mesh_obj.data.shape_keys.key_blocks[name]

    def for_each_head(predicate, displace_fn):
        offsets = [mathutils.Vector((0.0, 0.0, 0.0)) for _ in mesh_obj.data.vertices]
        count = 0
        for i, local in zip(indices, locals_):
            y_n = (local.y - y_min) / y_span
            z_n = (local.z - z_min) / z_span
            x = local.x
            if predicate(x, y_n, z_n):
                n = mesh_obj.data.vertices[i].normal
                offsets[i] = displace_fn(x, y_n, z_n, n)
                count += 1
        return offsets, count

    recipes = {
        "mouth_open": (
            lambda x, y_n, z_n: y_n < 0.45 and abs(x) < 0.08,
            lambda x, y_n, z_n, n: mathutils.Vector((0.0, 0.0, -1.2 * s)) + n * (0.4 * s),
        ),
        "mouth_close": (
            lambda x, y_n, z_n: y_n < 0.4 and abs(x) < 0.07,
            lambda x, y_n, z_n, n: mathutils.Vector((0.0, 0.0, 0.6 * s)),
        ),
        "mouth_wide": (
            lambda x, y_n, z_n: y_n < 0.5 and abs(x) > 0.02 and abs(x) < 0.1,
            lambda x, y_n, z_n, n: mathutils.Vector((1.2 * s if x > 0 else -1.2 * s, 0.0, 0.0)),
        ),
        "mouth_round": (
            lambda x, y_n, z_n: y_n < 0.48 and abs(x) < 0.05,
            lambda x, y_n, z_n, n: n * s + mathutils.Vector((0.0, 0.0, -0.4 * s)),
        ),
        "mouth_smile": (
            lambda x, y_n, z_n: y_n < 0.5 and abs(x) > 0.015,
            lambda x, y_n, z_n, n: mathutils.Vector(
                (1.4 * s if x > 0 else -1.4 * s, 0.0, 0.8 * s)
            ),
        ),
        "mouth_frown": (
            lambda x, y_n, z_n: y_n < 0.5 and abs(x) > 0.015,
            lambda x, y_n, z_n, n: mathutils.Vector(
                (1.0 * s if x > 0 else -1.0 * s, 0.0, -1.0 * s)
            ),
        ),
        "jaw_open": (
            lambda x, y_n, z_n: y_n < 0.42,
            lambda x, y_n, z_n, n: mathutils.Vector((0.0, 0.0, -1.8 * s)),
        ),
        "brow_up": (
            lambda x, y_n, z_n: y_n > 0.62 and y_n < 0.9,
            lambda x, y_n, z_n, n: mathutils.Vector((0.0, 0.0, 1.2 * s)),
        ),
        "brow_down": (
            lambda x, y_n, z_n: y_n > 0.62 and y_n < 0.9,
            lambda x, y_n, z_n, n: mathutils.Vector((0.0, 0.0, -1.0 * s)),
        ),
        "eye_blink_left": (
            lambda x, y_n, z_n: x > 0.01 and 0.48 < y_n < 0.72,
            lambda x, y_n, z_n, n: mathutils.Vector((0.0, 0.0, (-0.8 if y_n > 0.58 else 0.6) * s)),
        ),
        "eye_blink_right": (
            lambda x, y_n, z_n: x < -0.01 and 0.48 < y_n < 0.72,
            lambda x, y_n, z_n, n: mathutils.Vector((0.0, 0.0, (-0.8 if y_n > 0.58 else 0.6) * s)),
        ),
        "eye_wide": (
            lambda x, y_n, z_n: abs(x) > 0.01 and 0.5 < y_n < 0.75,
            lambda x, y_n, z_n, n: mathutils.Vector((0.0, 0.0, (0.6 if y_n > 0.6 else -0.4) * s)),
        ),
        "eye_squint": (
            lambda x, y_n, z_n: abs(x) > 0.01 and 0.5 < y_n < 0.75,
            lambda x, y_n, z_n, n: mathutils.Vector((0.0, 0.0, -0.5 * s)),
        ),
        "brow_inner_up": (
            lambda x, y_n, z_n: abs(x) < 0.04 and 0.62 < y_n < 0.88,
            lambda x, y_n, z_n, n: mathutils.Vector((0.0, 0.0, 1.4 * s)),
        ),
        "cheek_raise": (
            lambda x, y_n, z_n: abs(x) > 0.02 and 0.4 < y_n < 0.62,
            lambda x, y_n, z_n, n: n * (0.8 * s) + mathutils.Vector((0.0, 0.0, 0.6 * s)),
        ),
        "mouth_left": (
            lambda x, y_n, z_n: y_n < 0.5 and abs(x) < 0.09,
            lambda x, y_n, z_n, n: mathutils.Vector((-1.2 * s, 0.0, 0.0)),
        ),
        "mouth_right": (
            lambda x, y_n, z_n: y_n < 0.5 and abs(x) < 0.09,
            lambda x, y_n, z_n, n: mathutils.Vector((1.2 * s, 0.0, 0.0)),
        ),
        "nose_sneer": (
            lambda x, y_n, z_n: abs(x) < 0.05 and 0.45 < y_n < 0.7,
            lambda x, y_n, z_n, n: n * (0.6 * s) + mathutils.Vector((0.0, 0.0, 0.4 * s)),
        ),
    }

    # Axis note: Mixamo head-local may not match Z-up face. If deformations look
    # wrong, we also push along vertex normals which usually helps readability.
    for name, (pred, disp) in recipes.items():
        offsets, count = for_each_head(pred, disp)
        block = key(name)
        # Start from Basis positions
        basis = mesh_obj.data.shape_keys.key_blocks["Basis"]
        for i in range(len(block.data)):
            block.data[i].co = basis.data[i].co.copy()
        touched = 0
        for i, off in enumerate(offsets):
            if off.length_squared > 0:
                block.data[i].co += off
                touched += 1
        report("PASS", f"{name}: deformed {touched} verts (region hits={count})")

    # Never leave keys evaluated in the .blend — stacked values shred the face
    # and can bake into Basis if transforms are applied later.
    sk = mesh_obj.data.shape_keys
    if sk is not None:
        for block in sk.key_blocks:
            if block.name != "Basis":
                block.value = 0.0
        report("PASS", "Zeroed all shape-key values after write")

    if bpy.data.filepath:
        bpy.ops.wm.save_mainfile()
        report("PASS", f"Saved: {bpy.data.filepath}")

    report(
        "INFO",
        "Expressions use these morphs at runtime (FacialController). "
        "Re-export with npm run avatar:release after creating head clips.",
    )
    emit("RESULT", "OK")
    return 0


if __name__ == "__main__":
    sys.exit(improve_facial_shape_keys())
