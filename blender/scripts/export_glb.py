"""Export presenter.blend to blender/exports/presenter.glb using Blender's glTF exporter.

Writes only to the candidate export path under ``blender/exports/``. Never writes
directly to ``frontend/public/avatars/presenter.glb`` (promote manually after checks).

Run:

    blender --background blender/source/presenter.blend --python blender/scripts/export_glb.py
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


def export() -> int:
    """Export the current Blender scene as a candidate GLB under blender/exports/."""
    common = _load_common()
    bpy = common.require_bpy()

    output = common.candidate_presenter_glb()
    try:
        common.assert_export_path_allowed(output)
    except RuntimeError as exc:
        common.report("ERROR", str(exc))
        return 1

    output.parent.mkdir(parents=True, exist_ok=True)

    bpy.ops.export_scene.gltf(
        filepath=str(output),
        export_format="GLB",
        export_animations=True,
        export_morph=True,
        export_skins=True,
        export_apply=True,
        export_texcoords=True,
        export_normals=True,
        export_materials="EXPORT",
    )
    common.report("PASS", f"Exported candidate GLB: {output}")
    common.report(
        "INFO",
        f"Runtime asset is unchanged: {common.runtime_presenter_glb()} "
        "(copy/promote only after validation).",
    )
    return 0


if __name__ == "__main__":
    sys.exit(export())
