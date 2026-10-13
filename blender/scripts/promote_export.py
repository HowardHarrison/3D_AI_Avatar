"""Promote a validated temporary GLB to candidate + frontend runtime paths.

Runs in plain Python (no Blender). Re-runs ``validate_export`` on the temp file
and copies only when validation returns exit code 0.

    python blender/scripts/promote_export.py

Copies:

    blender/exports/tmp/presenter.glb
      → blender/exports/presenter.glb
      → frontend/public/avatars/presenter.glb

Exit codes: 0 on success, 1 if validation fails or copy fails.
"""

from __future__ import annotations

import shutil
import sys

import common
import validate_export


def promote() -> int:
    """Validate the temp GLB, then copy it to candidate and runtime locations."""
    tmp = common.tmp_presenter_glb()
    candidate = common.candidate_presenter_glb()
    runtime = common.runtime_presenter_glb()

    common.emit("FILE", str(tmp))
    common.report("INFO", "Running validate_export before promote...")

    status = validate_export.validate_export(tmp)
    if status != 0:
        common.report(
            "ERROR",
            "Validation failed — runtime and candidate assets were not changed.",
        )
        common.emit("RESULT", "ERROR")
        return 1

    try:
        common.assert_export_path_allowed(tmp)
    except RuntimeError as exc:
        common.report("ERROR", str(exc))
        return 1

    candidate.parent.mkdir(parents=True, exist_ok=True)
    runtime.parent.mkdir(parents=True, exist_ok=True)

    shutil.copy2(tmp, candidate)
    common.report("PASS", f"Wrote candidate: {candidate}")

    shutil.copy2(tmp, runtime)
    common.report("PASS", f"Wrote runtime: {runtime}")

    common.emit("RESULT", "PASS")
    return 0


if __name__ == "__main__":
    sys.exit(promote())
