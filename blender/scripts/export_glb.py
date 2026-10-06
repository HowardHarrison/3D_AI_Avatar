"""Export presenter.blend to blender/exports/presenter.glb using Blender's glTF exporter.

Run:

    blender --background blender/source/presenter.blend --python blender/scripts/export_glb.py
"""

from __future__ import annotations

import sys
from pathlib import Path


def export() -> int:
    """Export the current Blender scene as a GLB next to this repository's blender folder."""
    try:
        import bpy  # type: ignore
    except ImportError:
        print("ERROR: This script must run inside Blender (bpy is missing).")
        return 1

    repo_blender = Path(__file__).resolve().parents[1]
    output = repo_blender / "exports" / "presenter.glb"
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
    print(f"PASS: Exported {output}")
    return 0


if __name__ == "__main__":
    sys.exit(export())
