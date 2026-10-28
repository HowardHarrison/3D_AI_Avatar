"""Validate a temporary presenter GLB before promotion to runtime assets.

Runs in plain Python (no Blender). Parses the GLB JSON chunk with the stdlib
only — no extra packages.

Default path: ``blender/exports/tmp/presenter.glb``

    python blender/scripts/validate_export.py
    python blender/scripts/validate_export.py path/to/other.glb

Exit codes: 0 if no ERROR results, 1 otherwise. Missing optional clips are WARNING.
"""

from __future__ import annotations

import json
import struct
import sys
from pathlib import Path

import common
from contracts import (
    OPTIONAL_ANIMATIONS,
    OPTIONAL_SHAPE_KEYS,
    REQUIRED_ANIMATIONS,
    REQUIRED_SHAPE_KEYS,
)

GLB_MAGIC = 0x46546C67
JSON_CHUNK_TYPE = 0x4E4F534A


def read_glb_json(path: Path) -> dict:
    """Read and parse the JSON chunk from a GLB 2.0 file.

    Parameters:
        path: Path to a ``.glb`` file.

    Returns:
        Parsed glTF JSON root object.

    Raises:
        ValueError: If the file is not a valid GLB with a JSON chunk.
        OSError: If the file cannot be read.
    """
    data = path.read_bytes()
    if len(data) < 20:
        raise ValueError("File too small to be a GLB")

    magic, version, _total_length = struct.unpack_from("<III", data, 0)
    if magic != GLB_MAGIC:
        raise ValueError("Not a GLB file (bad magic)")
    if version != 2:
        raise ValueError(f"Unsupported GLB version: {version}")

    chunk_length, chunk_type = struct.unpack_from("<II", data, 12)
    if chunk_type != JSON_CHUNK_TYPE:
        raise ValueError("First GLB chunk is not JSON")

    json_start = 20
    json_end = json_start + chunk_length
    if json_end > len(data):
        raise ValueError("GLB JSON chunk extends past end of file")

    raw = data[json_start:json_end].split(b"\x00", 1)[0]
    return json.loads(raw.decode("utf-8"))


def _animation_names(gltf: dict) -> set[str]:
    """Collect animation clip names from the glTF document."""
    names: set[str] = set()
    for index, anim in enumerate(gltf.get("animations") or []):
        name = anim.get("name")
        names.add(name if name else f"animation_{index}")
    return names


def _shape_key_names(gltf: dict) -> set[str]:
    """Collect morph target names from mesh extras.targetNames when present."""
    names: set[str] = set()
    for mesh in gltf.get("meshes") or []:
        extras = mesh.get("extras") or {}
        target_names = extras.get("targetNames") or []
        for name in target_names:
            if isinstance(name, str) and name and name != "Basis":
                names.add(name)
        # Fallback: unnamed targets still count as "has morphs"
        for prim in mesh.get("primitives") or []:
            targets = prim.get("targets") or []
            if targets and not target_names:
                names.add(f"(unnamed_targets:{len(targets)})")
    return names


def validate_export(glb_path: Path | None = None) -> int:
    """Validate a GLB export and return a process exit code.

    Parameters:
        glb_path: File to check; defaults to ``exports/tmp/presenter.glb``.
    """
    path = glb_path or common.tmp_presenter_glb()
    common.emit("FILE", str(path))

    errors = 0
    warnings = 0

    if not path.is_file():
        common.report("ERROR", f"GLB not found: {path}")
        common.emit("RESULT", "ERROR")
        return 1

    size = path.stat().st_size
    if size < 64:
        common.report("ERROR", f"GLB is suspiciously small ({size} bytes)")
        errors += 1
    else:
        common.report("PASS", f"GLB exists ({size} bytes)")

    try:
        gltf = read_glb_json(path)
    except (ValueError, OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        common.report("ERROR", f"Failed to parse GLB JSON: {exc}")
        common.emit("RESULT", "ERROR")
        return 1

    meshes = gltf.get("meshes") or []
    if not meshes:
        common.report("ERROR", "No meshes in GLB")
        errors += 1
    else:
        common.report("PASS", f"Meshes: {len(meshes)}")

    nodes = gltf.get("nodes") or []
    if not nodes:
        common.report("ERROR", "No nodes in GLB")
        errors += 1
    else:
        common.report("PASS", f"Nodes: {len(nodes)}")

    materials = gltf.get("materials") or []
    if materials:
        common.report("PASS", f"Materials: {len(materials)}")
    else:
        common.report("WARNING", "No materials in GLB")
        warnings += 1

    skins = gltf.get("skins") or []
    if skins:
        common.report("PASS", f"Skins: {len(skins)}")
    else:
        common.report("WARNING", "No skins in GLB (rig may be missing)")
        warnings += 1

    shape_keys = _shape_key_names(gltf)
    if shape_keys:
        common.report("PASS", f"Morph / shape-key names found: {len(shape_keys)}")
    else:
        common.report("WARNING", "No morph target names found (extras.targetNames missing)")
        warnings += 1

    for name in REQUIRED_SHAPE_KEYS:
        if name in shape_keys:
            common.report("PASS", f"Shape key present: {name}")
        else:
            common.report("ERROR", f"Required shape key missing: {name}")
            errors += 1

    optional_face = [n for n in OPTIONAL_SHAPE_KEYS if n in shape_keys]
    if not optional_face:
        common.report(
            "WARNING",
            "Optional face shape keys not present "
            f"({', '.join(OPTIONAL_SHAPE_KEYS)}). "
            "Mixamo does not supply these — add in Blender after import.",
        )
        warnings += 1
    else:
        for name in OPTIONAL_SHAPE_KEYS:
            if name in shape_keys:
                common.report("PASS", f"Optional shape key present: {name}")
            else:
                common.report("WARNING", f"Optional shape key missing: {name}")
                warnings += 1

    clip_names = _animation_names(gltf)
    if clip_names:
        common.report("PASS", f"Animation clips: {len(clip_names)}")
        for name in sorted(clip_names):
            common.emit("ACTION", name)
    else:
        common.report("ERROR", "No animations in GLB")
        errors += 1

    for name in REQUIRED_ANIMATIONS:
        if name in clip_names:
            common.report("PASS", f"Animation present: {name}")
        else:
            common.report("ERROR", f"Required animation missing: {name}")
            errors += 1

    for name in OPTIONAL_ANIMATIONS:
        if name not in clip_names:
            common.report("WARNING", f"Optional animation missing: {name}")
            warnings += 1

    common.emit("SUMMARY", f"errors={errors} warnings={warnings}")
    if errors:
        common.emit("RESULT", "ERROR")
        return 1
    common.emit("RESULT", "PASS" if warnings == 0 else "WARNING")
    return 0


def _cli_path() -> Path | None:
    """Return an optional GLB path from argv (first non-flag argument)."""
    args = [a for a in sys.argv[1:] if not a.startswith("-")]
    if not args:
        return None
    return Path(args[0])


if __name__ == "__main__":
    sys.exit(validate_export(_cli_path()))
