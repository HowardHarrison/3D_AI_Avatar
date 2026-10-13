"""Shared paths and safety helpers for Blender automation scripts.

Importable from other scripts in this folder when they run inside Blender
(``blender --background ... --python ...``) or, for path helpers only, from
plain Python.

These helpers do not score the avatar naming contract — see ``contracts.py``
and ``validate_rig.py`` for that.
"""

from __future__ import annotations

import importlib.util
import shutil
import sys
from datetime import datetime
from pathlib import Path
from types import ModuleType


def scripts_dir() -> Path:
    """Return ``blender/scripts`` (this file's directory)."""
    return Path(__file__).resolve().parent


def blender_dir() -> Path:
    """Return the repository ``blender/`` directory."""
    return scripts_dir().parent


def repo_root() -> Path:
    """Return the repository root (parent of ``blender/``)."""
    return blender_dir().parent


def presenter_blend_path() -> Path:
    """Return the expected path to ``blender/source/presenter.blend``."""
    return blender_dir() / "source" / "presenter.blend"


def versions_dir() -> Path:
    """Return ``blender/source/versions`` for recoverable .blend copies."""
    return blender_dir() / "source" / "versions"


def exports_dir() -> Path:
    """Return ``blender/exports`` (candidate GLB output)."""
    return blender_dir() / "exports"


def exports_tmp_dir() -> Path:
    """Return ``blender/exports/tmp`` for unvalidated export output."""
    return exports_dir() / "tmp"


def tmp_presenter_glb() -> Path:
    """Return ``blender/exports/tmp/presenter.glb`` (pre-validation export)."""
    return exports_tmp_dir() / "presenter.glb"


def candidate_presenter_glb() -> Path:
    """Return ``blender/exports/presenter.glb`` (validated export, not yet runtime)."""
    return exports_dir() / "presenter.glb"


def runtime_presenter_glb() -> Path:
    """Return the frontend runtime asset path that must not be overwritten blindly."""
    return repo_root() / "frontend" / "public" / "avatars" / "presenter.glb"


def emit(kind: str, message: str) -> None:
    """Print one ``KIND: message`` line for agents and developers to parse."""
    print(f"{kind}: {message}")


def report(level: str, message: str) -> None:
    """Print a status line (``PASS``, ``WARNING``, ``ERROR``, or ``INFO``)."""
    emit(level, message)


def require_bpy():
    """Import and return ``bpy``, or print an error and exit the process with code 1."""
    try:
        import bpy  # type: ignore
    except ImportError:
        report("ERROR", "This script must run inside Blender (bpy is missing).")
        sys.exit(1)
    return bpy


def load_scripts_module(module_stem: str) -> ModuleType:
    """Load another module from ``blender/scripts`` by file stem (e.g. ``contracts``)."""
    path = scripts_dir() / f"{module_stem}.py"
    if not path.is_file():
        raise RuntimeError(f"Unable to find blender/scripts/{module_stem}.py")
    spec = importlib.util.spec_from_file_location(module_stem, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load blender/scripts/{module_stem}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def assert_export_path_allowed(path: Path) -> None:
    """Refuse writes that would replace the live frontend runtime GLB.

    Parameters:
        path: Intended export destination.

    Raises:
        RuntimeError: If ``path`` resolves to the runtime ``presenter.glb``.
    """
    resolved = path.resolve()
    runtime = runtime_presenter_glb().resolve()
    if resolved == runtime:
        raise RuntimeError(
            f"Refusing to write directly to runtime asset {runtime}. "
            "Export to blender/exports/tmp/ then run validate_export.py and promote_export.py."
        )


def save_versioned_blend(*, label: str = "pre_edit") -> Path:
    """Save the open .blend, then copy it into ``blender/source/versions/``.

    Creates a timestamped recoverable copy before structural edits. Does not
    change the working file path (still ``presenter.blend`` after copy).

    Parameters:
        label: Short tag included in the backup filename (sanitized).

    Returns:
        Path to the written backup file.

    Raises:
        RuntimeError: If the blend is unsaved, missing on disk, or ``bpy`` is unavailable.
    """
    try:
        import bpy  # type: ignore
    except ImportError as exc:
        raise RuntimeError("save_versioned_blend requires Blender (bpy is missing).") from exc

    if not bpy.data.filepath:
        raise RuntimeError(
            "Cannot backup: blend file is unsaved. Save as blender/source/presenter.blend first."
        )

    src = Path(bpy.data.filepath)
    if not src.is_file():
        raise RuntimeError(f"Cannot backup: blend path does not exist on disk: {src}")

    bpy.ops.wm.save_mainfile()

    dest_dir = versions_dir()
    dest_dir.mkdir(parents=True, exist_ok=True)

    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_label = "".join(c if c.isalnum() or c in "-_" else "_" for c in label)[:40] or "backup"
    dest = dest_dir / f"{stamp}_{safe_label}_{src.name}"

    shutil.copy2(src, dest)
    report("PASS", f"Saved recoverable version: {dest}")
    return dest
