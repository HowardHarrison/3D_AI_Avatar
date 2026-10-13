"""Inventory the open Blender scene for AI-agent and developer inspection.

Prints machine-friendly prefixed lines (no contract PASS/FAIL scoring).
Use validate_rig.py to check naming contracts after inspection.

Run from the repository root:

    blender --background blender/source/presenter.blend --python blender/scripts/inspect_scene.py

If presenter.blend does not exist yet, you can smoke-test against Blender's
default startup scene (expect ERROR: no armature):

    blender --background --python blender/scripts/inspect_scene.py

Exit codes: 0 when the scene has objects and at least one armature; 1 otherwise.
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


def inspect_scene() -> int:
    """Walk the open .blend and print an inventory; return process exit code."""
    common = _load_common()
    bpy = common.require_bpy()
    emit = common.emit

    blend_path = bpy.data.filepath or "(unsaved / default startup)"
    emit("FILE", blend_path)
    emit("BLENDER", bpy.app.version_string)

    objects = list(bpy.data.objects)
    if not objects:
        emit("ERROR", "No objects in the file (scene is empty).")
        emit("RESULT", "ERROR")
        return 1

    emit("SECTION", "objects")
    for obj in sorted(objects, key=lambda o: o.name):
        parent = obj.parent.name if obj.parent else "-"
        emit("OBJECT", f"{obj.name}|type={obj.type}|parent={parent}")

    emit("SECTION", "collections")
    for collection in sorted(bpy.data.collections, key=lambda c: c.name):
        child_names = ", ".join(sorted(o.name for o in collection.objects)) or "-"
        emit("COLLECTION", f"{collection.name}|objects={child_names}")

    emit("SECTION", "materials")
    materials = list(bpy.data.materials)
    if not materials:
        emit("INFO", "No materials in bpy.data.materials.")
    else:
        for mat in sorted(materials, key=lambda m: m.name):
            users = mat.users
            emit("MATERIAL", f"{mat.name}|users={users}")

    armatures = [obj for obj in objects if obj.type == "ARMATURE"]
    emit("SECTION", "armatures")
    if not armatures:
        emit("ERROR", "No armature found.")
    else:
        for arm in sorted(armatures, key=lambda o: o.name):
            bone_count = len(arm.data.bones)
            emit("ARMATURE", f"{arm.name}|bones={bone_count}")
            emit("SECTION", f"bones:{arm.name}")
            for bone in sorted(arm.data.bones, key=lambda b: b.name):
                parent = bone.parent.name if bone.parent else "-"
                emit("BONE", f"{bone.name}|parent={parent}")

    meshes = [obj for obj in objects if obj.type == "MESH"]
    emit("SECTION", "shape_keys")
    if not meshes:
        emit("INFO", "No mesh objects.")
    else:
        any_keys = False
        for mesh_obj in sorted(meshes, key=lambda o: o.name):
            key = mesh_obj.data.shape_keys
            if key is None:
                emit("INFO", f"{mesh_obj.name}|shape_keys=none")
                continue
            any_keys = True
            names = [block.name for block in key.key_blocks]
            emit("MESH_KEYS", f"{mesh_obj.name}|count={len(names)}")
            for name in names:
                emit("SHAPE_KEY", f"{mesh_obj.name}|{name}")
        if not any_keys:
            emit("INFO", "No shape keys on any mesh.")

    emit("SECTION", "animations")
    action_names = sorted({action.name for action in bpy.data.actions})
    if action_names:
        for name in action_names:
            emit("ACTION", name)
    else:
        emit("INFO", "No actions in bpy.data.actions.")

    nla_reported = False
    for arm in armatures:
        anim = arm.animation_data
        if anim is None or not anim.nla_tracks:
            continue
        for track in anim.nla_tracks:
            for strip in track.strips:
                nla_reported = True
                action_name = strip.action.name if strip.action else "-"
                emit(
                    "NLA_STRIP",
                    f"armature={arm.name}|track={track.name}|strip={strip.name}|action={action_name}",
                )
    if armatures and not nla_reported:
        emit("INFO", "No NLA strips on armatures.")

    emit("SECTION", "summary")
    emit("COUNT", f"objects={len(objects)}")
    emit("COUNT", f"collections={len(list(bpy.data.collections))}")
    emit("COUNT", f"materials={len(materials)}")
    emit("COUNT", f"armatures={len(armatures)}")
    emit("COUNT", f"meshes={len(meshes)}")
    emit("COUNT", f"actions={len(action_names)}")

    if not armatures:
        emit("RESULT", "ERROR")
        return 1

    emit("RESULT", "OK")
    return 0


if __name__ == "__main__":
    sys.exit(inspect_scene())
