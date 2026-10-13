"""Create a contract-compliant learning scaffold at blender/source/presenter.blend.

This is **not** a production news presenter. It is a low-poly stand-in with the
required bones, facial shape-key names, materials, and stub animations so the
Blender → validate → export → promote pipeline can be exercised before a
licensed character is adopted.

    blender --background --python blender/scripts/scaffold_presenter_blend.py

Overwrite an existing presenter.blend:

    blender --background --python blender/scripts/scaffold_presenter_blend.py -- --force

Skip validate/export at the end:

    blender --background --python blender/scripts/scaffold_presenter_blend.py -- --force --skip-export
"""

from __future__ import annotations

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


def _clear_scene(bpy) -> None:
    """Remove all objects, orphan meshes, armatures, actions, and materials."""
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    for collection in (
        bpy.data.meshes,
        bpy.data.armatures,
        bpy.data.actions,
        bpy.data.materials,
        bpy.data.curves,
    ):
        for block in list(collection):
            collection.remove(block)


def _add_bone(edit_bones, name: str, parent, head, tail):
    """Create one edit bone with optional parent."""
    bone = edit_bones.new(name)
    bone.head = head
    bone.tail = tail
    if parent is not None:
        bone.parent = parent
        bone.use_connect = False
    return bone


def _build_armature(bpy, contracts):
    """Create PresenterArmature with required (and optional leg) bones."""
    arm_data = bpy.data.armatures.new("PresenterArmature")
    arm_obj = bpy.data.objects.new("PresenterArmature", arm_data)
    bpy.context.collection.objects.link(arm_obj)
    bpy.context.view_layer.objects.active = arm_obj
    bpy.ops.object.mode_set(mode="EDIT")
    eb = arm_data.edit_bones

    hips = _add_bone(eb, "Hips", None, (0, 0, 1.0), (0, 0, 1.1))
    spine = _add_bone(eb, "Spine", hips, (0, 0, 1.15), (0, 0, 1.3))
    chest = _add_bone(eb, "Chest", spine, (0, 0, 1.35), (0, 0, 1.5))
    neck = _add_bone(eb, "Neck", chest, (0, 0, 1.52), (0, 0, 1.6))
    _add_bone(eb, "Head", neck, (0, 0, 1.62), (0, 0, 1.75))

    l_shoulder = _add_bone(eb, "LeftShoulder", chest, (0.05, 0, 1.48), (0.15, 0, 1.48))
    l_upper = _add_bone(eb, "LeftUpperArm", l_shoulder, (0.2, 0, 1.45), (0.4, 0, 1.25))
    l_lower = _add_bone(eb, "LeftLowerArm", l_upper, (0.42, 0, 1.22), (0.55, 0, 1.05))
    _add_bone(eb, "LeftHand", l_lower, (0.57, 0, 1.02), (0.65, 0, 0.98))

    r_shoulder = _add_bone(eb, "RightShoulder", chest, (-0.05, 0, 1.48), (-0.15, 0, 1.48))
    r_upper = _add_bone(eb, "RightUpperArm", r_shoulder, (-0.2, 0, 1.45), (-0.4, 0, 1.25))
    r_lower = _add_bone(eb, "RightLowerArm", r_upper, (-0.42, 0, 1.22), (-0.55, 0, 1.05))
    _add_bone(eb, "RightHand", r_lower, (-0.57, 0, 1.02), (-0.65, 0, 0.98))

    # Optional legs (validate_rig WARNING if missing — include to reduce noise)
    for side, sign in (("Left", 1.0), ("Right", -1.0)):
        upper = _add_bone(
            eb,
            f"{side}UpperLeg",
            hips,
            (0.1 * sign, 0, 0.95),
            (0.12 * sign, 0, 0.55),
        )
        lower = _add_bone(
            eb,
            f"{side}LowerLeg",
            upper,
            (0.12 * sign, 0, 0.52),
            (0.12 * sign, 0, 0.15),
        )
        _add_bone(eb, f"{side}Foot", lower, (0.12 * sign, 0.05, 0.12), (0.12 * sign, 0.15, 0.05))

    bpy.ops.object.mode_set(mode="OBJECT")

    # Sanity: required bones present
    names = {b.name for b in arm_data.bones}
    missing = [b for b in contracts.REQUIRED_BONES if b not in names]
    if missing:
        raise RuntimeError(f"Scaffold failed to create bones: {missing}")
    return arm_obj


def _build_meshes(bpy, arm_obj, contracts):
    """Create simple body + head meshes with required shape keys."""
    # Body
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 1.2))
    body = bpy.context.active_object
    body.name = "PresenterBody"
    body.scale = (0.35, 0.2, 0.55)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

    mat_body = bpy.data.materials.new("Suit")
    mat_body.diffuse_color = (0.05, 0.15, 0.45, 1.0)
    if mat_body.node_tree:
        node = next(
            (n for n in mat_body.node_tree.nodes if n.type == "BSDF_PRINCIPLED"),
            None,
        )
        if node and node.inputs.get("Base Color"):
            node.inputs["Base Color"].default_value = (0.05, 0.15, 0.45, 1.0)
    body.data.materials.append(mat_body)

    # Head
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.12, location=(0, 0, 1.68))
    head = bpy.context.active_object
    head.name = "PresenterHead"
    mat_head = bpy.data.materials.new("Skin")
    mat_head.diffuse_color = (0.8, 0.62, 0.5, 1.0)
    if mat_head.node_tree:
        node = next(
            (n for n in mat_head.node_tree.nodes if n.type == "BSDF_PRINCIPLED"),
            None,
        )
        if node and node.inputs.get("Base Color"):
            node.inputs["Base Color"].default_value = (0.8, 0.62, 0.5, 1.0)
    head.data.materials.append(mat_head)

    # Shape keys on head (tiny deltas so names exist for the contract)
    head.shape_key_add(name="Basis", from_mix=False)
    import mathutils

    for key_name in contracts.REQUIRED_SHAPE_KEYS:
        key = head.shape_key_add(name=key_name, from_mix=False)
        # Nudge a few vertices so the key is not identical to Basis
        for i, vert in enumerate(key.data):
            if i % 7 == 0:
                vert.co += mathutils.Vector((0.001, 0.0, 0.001))

    # Parent to armature (no full skinning — learning scaffold)
    for obj in (body, head):
        obj.parent = arm_obj
        obj.parent_type = "ARMATURE"

    return body, head


def scaffold(argv: list[str] | None = None) -> int:
    """Build and save the learning presenter.blend; return exit code."""
    import argparse

    common = _load_common()
    bpy = common.require_bpy()
    emit = common.emit
    report = common.report
    contracts = common.load_scripts_module("contracts")

    parser = argparse.ArgumentParser(description="Scaffold a contract-compliant presenter.blend")
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing blender/source/presenter.blend",
    )
    parser.add_argument("--skip-validate", action="store_true")
    parser.add_argument("--skip-export", action="store_true")
    parser.add_argument(
        "--skip-animations",
        action="store_true",
        help="Do not create required stub clips (not recommended).",
    )
    try:
        args = parser.parse_args(_script_argv(argv))
    except SystemExit as exc:
        return exc.code if isinstance(exc.code, int) else 1

    out = common.presenter_blend_path()
    emit("FILE", str(out))

    if out.is_file() and not args.force:
        report(
            "ERROR",
            f"Refusing to overwrite existing {out}. Pass --force, or adopt a licensed character instead.",
        )
        emit("RESULT", "ERROR")
        return 1

    if out.is_file() and args.force:
        report("WARNING", f"Overwriting existing scaffold/source blend: {out}")

    report("INFO", "Clearing scene and building learning scaffold (not a production character)...")
    _clear_scene(bpy)

    try:
        arm = _build_armature(bpy, contracts)
        _build_meshes(bpy, arm, contracts)
    except RuntimeError as exc:
        report("ERROR", str(exc))
        emit("RESULT", "ERROR")
        return 1

    out.parent.mkdir(parents=True, exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(out))
    report("PASS", f"Saved scaffold blend: {out}")

    if not args.skip_animations:
        create_animation = common.load_scripts_module("create_animation")
        report("INFO", "Creating required stub animations...")
        status = create_animation.create_animation(
            [
                "create_animation.py",
                "--create-all-required",
                "--no-backup",
                "--skip-validate",
                "--skip-export",
            ]
        )
        if status != 0:
            report("ERROR", "Failed to create required stub animations.")
            emit("RESULT", "ERROR")
            return 1
        bpy.ops.wm.save_mainfile()
        report("PASS", "Required stub animations created and blend re-saved.")
    else:
        report("WARNING", "Skipped stub animations (--skip-animations).")

    if not args.skip_validate:
        validate_rig = common.load_scripts_module("validate_rig")
        report("INFO", "Running validate_rig...")
        if validate_rig.validate() != 0:
            report("ERROR", "validate_rig failed on scaffold.")
            emit("RESULT", "ERROR")
            return 1
    else:
        report("WARNING", "Skipped validate_rig.")

    if not args.skip_export:
        export_glb = common.load_scripts_module("export_glb")
        report("INFO", "Exporting scaffold to temp GLB...")
        if export_glb.export() != 0:
            report("ERROR", "Temp export failed.")
            emit("RESULT", "ERROR")
            return 1
        report(
            "INFO",
            "Optional promote: python blender/scripts/validate_export.py "
            "&& python blender/scripts/promote_export.py",
        )
    else:
        report("WARNING", "Skipped temp export.")

    report(
        "INFO",
        "Scaffold only. For a real presenter, import a licensed humanoid and follow "
        "the adoption checklist in docs/blender-pipeline.md.",
    )
    emit("RESULT", "OK")
    return 0


if __name__ == "__main__":
    sys.exit(scaffold())
