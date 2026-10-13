"""Change one material base color in the open .blend (targeted, reversible edit).

Always inspect materials before changing them. Default flow:

1. Resolve the named material (error if missing)
2. ``save_versioned_blend`` backup under ``blender/source/versions/``
3. Set Principled BSDF Base Color (or ``diffuse_color`` fallback)
4. Save the working ``.blend``
5. Run ``validate_rig`` (optional skip)
6. Export to ``blender/exports/tmp/presenter.glb`` (optional skip)

List materials only:

    blender --background blender/source/presenter.blend --python blender/scripts/modify_materials.py -- --list

Change a color (RGB 0-1):

    blender --background blender/source/presenter.blend --python blender/scripts/modify_materials.py -- --material Suit --color 0.05,0.15,0.45

Smoke-test on Blender's default startup (unsaved — use ``--no-backup``):

    blender --background --python blender/scripts/modify_materials.py -- --list
    blender --background --python blender/scripts/modify_materials.py -- --material Material --color 1,0,0 --no-backup --skip-validate --skip-export

After a real export, promote with:

    python blender/scripts/validate_export.py
    python blender/scripts/promote_export.py
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
    # Plain ``python modify_materials.py ...`` (no Blender)
    return args[1:]


def _parse_color(text: str) -> tuple[float, float, float, float]:
    """Parse ``R,G,B`` or ``R,G,B,A`` floats in 0-1 range."""
    parts = [p.strip() for p in text.split(",")]
    if len(parts) not in (3, 4):
        raise ValueError("Color must be R,G,B or R,G,B,A (comma-separated floats 0-1)")
    values = [float(p) for p in parts]
    if len(values) == 3:
        values.append(1.0)
    for value in values:
        if value < 0.0 or value > 1.0:
            raise ValueError(f"Color channel out of range 0-1: {value}")
    return values[0], values[1], values[2], values[3]


def _material_has_nodes(mat) -> bool:
    """Return True when the material has a node tree (Blender 5+ safe check)."""
    # Avoid Material.use_nodes — deprecated in Blender 5.2, removed in 6.0.
    return mat.node_tree is not None


def _read_base_color(mat) -> str:
    """Return a short string describing the material's current base color."""
    if _material_has_nodes(mat):
        for node in mat.node_tree.nodes:
            if node.type != "BSDF_PRINCIPLED":
                continue
            socket = node.inputs.get("Base Color")
            if socket is not None:
                r, g, b, a = socket.default_value
                return f"principled=({r:.3f},{g:.3f},{b:.3f},{a:.3f})"
    r, g, b, a = mat.diffuse_color
    return f"diffuse=({r:.3f},{g:.3f},{b:.3f},{a:.3f})"


def _set_base_color(mat, rgba: tuple[float, float, float, float]) -> str:
    """Set base color on Principled BSDF when possible; else diffuse_color.

    Returns:
        Which path was used: ``principled`` or ``diffuse``.
    """
    if _material_has_nodes(mat):
        for node in mat.node_tree.nodes:
            if node.type != "BSDF_PRINCIPLED":
                continue
            socket = node.inputs.get("Base Color")
            if socket is not None:
                socket.default_value = rgba
                return "principled"
    mat.diffuse_color = rgba
    return "diffuse"


def _list_materials(bpy, emit) -> int:
    """Print materials in the open file and return exit code."""
    materials = list(bpy.data.materials)
    emit("SECTION", "materials")
    if not materials:
        emit("ERROR", "No materials in the file.")
        emit("RESULT", "ERROR")
        return 1
    for mat in sorted(materials, key=lambda m: m.name):
        emit(
            "MATERIAL",
            f"{mat.name}|users={mat.users}|color={_read_base_color(mat)}|nodes={_material_has_nodes(mat)}",
        )
    emit("COUNT", f"materials={len(materials)}")
    emit("RESULT", "OK")
    return 0


def _build_parser() -> argparse.ArgumentParser:
    """Create CLI parser for material list/modify flags."""
    parser = argparse.ArgumentParser(
        description="List or modify a Blender material base color (safe, targeted).",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List materials and exit (no changes).",
    )
    parser.add_argument(
        "--material",
        type=str,
        default=None,
        help="Exact material name to modify.",
    )
    parser.add_argument(
        "--color",
        type=str,
        default=None,
        help="New base color as R,G,B or R,G,B,A (floats 0-1).",
    )
    parser.add_argument(
        "--no-backup",
        action="store_true",
        help="Skip versioned .blend backup (only for unsaved smoke tests).",
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


def modify_materials(argv: list[str] | None = None) -> int:
    """List or modify materials in the open Blender file; return exit code."""
    common = _load_common()
    bpy = common.require_bpy()
    emit = common.emit
    report = common.report

    parser = _build_parser()
    try:
        args = parser.parse_args(_script_argv(argv))
    except SystemExit as exc:
        code = exc.code if isinstance(exc.code, int) else 1
        return code

    blend_path = bpy.data.filepath or "(unsaved / default startup)"
    emit("FILE", blend_path)

    if args.list:
        return _list_materials(bpy, emit)

    if not args.material or not args.color:
        report(
            "ERROR",
            "Provide --material NAME and --color R,G,B (or use --list). "
            "Pass flags after blender's -- separator.",
        )
        emit("RESULT", "ERROR")
        return 1

    try:
        rgba = _parse_color(args.color)
    except ValueError as exc:
        report("ERROR", str(exc))
        emit("RESULT", "ERROR")
        return 1

    mat = bpy.data.materials.get(args.material)
    if mat is None:
        available = ", ".join(sorted(m.name for m in bpy.data.materials)) or "(none)"
        report("ERROR", f"Material not found: {args.material}")
        report("INFO", f"Available materials: {available}")
        emit("RESULT", "ERROR")
        return 1

    report("INFO", f"Before: {mat.name} {_read_base_color(mat)}")

    if args.no_backup:
        report("WARNING", "Skipping versioned backup (--no-backup).")
    else:
        try:
            common.save_versioned_blend(label=f"pre_material_{mat.name}")
        except RuntimeError as exc:
            report("ERROR", str(exc))
            report("INFO", "Save the .blend first, or pass --no-backup for a disposable smoke test.")
            emit("RESULT", "ERROR")
            return 1

    path_used = _set_base_color(mat, rgba)
    report("PASS", f"Set {mat.name} via {path_used}: {_read_base_color(mat)}")

    if bpy.data.filepath:
        bpy.ops.wm.save_mainfile()
        report("PASS", f"Saved working blend: {bpy.data.filepath}")
    else:
        report("WARNING", "Working blend is unsaved; color change exists only in this Blender process.")

    if not args.skip_validate:
        validate_rig = common.load_scripts_module("validate_rig")
        report("INFO", "Running validate_rig...")
        status = validate_rig.validate()
        if status != 0:
            report(
                "ERROR",
                "validate_rig failed after material edit. "
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
            report("ERROR", "Temp export failed after material edit.")
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
    sys.exit(modify_materials())
