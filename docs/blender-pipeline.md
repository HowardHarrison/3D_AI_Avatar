# Blender asset pipeline

Blender is the **authoring and automation** environment for structural 3D changes.
The browser never opens `.blend` files. The only runtime asset is a validated
`presenter.glb`.

Authoring details and naming contracts: [blender/README.md](../blender/README.md)

Architecture context: [architecture.md](architecture.md)

## Scripts location (important)

Phase 1 MVP text sometimes names this folder `blender/automation/`.
**This repository keeps `blender/scripts/`** as the automation directory.

Do not rename or duplicate into `automation/` until a later cleanup step.
When the MVP mentions `blender/automation/*.py`, use `blender/scripts/*.py`.

| MVP name | Actual path |
| --- | --- |
| `blender/automation/` | `blender/scripts/` |
| `inspect_scene.py` | `blender/scripts/inspect_scene.py` |
| `validate_rig.py` | `blender/scripts/validate_rig.py` |
| `export_glb.py` | `blender/scripts/export_glb.py` |
| `validate_export.py` | `blender/scripts/validate_export.py` |
| `promote_export.py` | `blender/scripts/promote_export.py` |

## Prerequisites

- **Blender 3.6 LTS, 4.x, or 5.x** installed locally
- The `blender` executable available on your **PATH** so headless commands work
  from the repository root
- A source file at `blender/source/presenter.blend` for a full presenter inventory
  (optional until you adopt a real character; use the placeholder GLB for web
  work without Blender)

### Check Blender CLI

From the repository root:

```bash
blender --version
```

You should see a version line (3.6.x, 4.x, or 5.x). If the command is not found:

- **Windows:** add Blender’s install folder to PATH, or call the full path, e.g.
  `"C:\Program Files\Blender Foundation\Blender 5.2\blender.exe"`
- **macOS / Linux:** ensure the Blender binary is on PATH (or use the full path
  to the app bundle executable)

All headless examples below assume `blender` resolves on PATH. Substitute your
full path if needed.

### When you do not need Blender

Behavior-only changes (gestures, idle timing, expressions, camera) belong in
JSON / TypeScript under `frontend/`. Use Blender only for geometry, rig,
materials baked into the asset, shape keys, skin weights, or authored clips.

Without Blender, generate a contract-compliant stand-in:

```bash
python blender/scripts/generate_placeholder_glb.py
```

Then copy `blender/exports/presenter.glb` → `frontend/public/avatars/presenter.glb`.

## Safe automation sequence

Structural edits must follow this order. Do not skip inspection or overwrite a
working runtime GLB with an unvalidated export.

```text
Inspect source project
        |
        v
Check required objects and materials
        |
        v
Apply a targeted modification
        |
        v
Save a recoverable project version
        |
        v
Validate scene and rig
        |
        v
Export GLB to a temporary location
        |
        v
Validate exported asset
        |
        v
Promote validated export to runtime assets
```

Rules:

1. **Inspect before modify** — never assume object, bone, or material names.
2. **Backup before risky edits** — call `save_versioned_blend()` from
   `blender/scripts/common.py` (writes timestamped copies under
   `blender/source/versions/`). Do not start structural edits on an unsaved file.
3. **Validate the scene** before export (`validate_rig.py`).
4. **Export to a temp path** — `export_glb.py` writes
   `blender/exports/tmp/presenter.glb` only. It **refuses** to write directly to
   the frontend runtime GLB.
5. **Validate then promote** — `validate_export.py` checks the temp GLB;
   `promote_export.py` copies to `blender/exports/presenter.glb` and
   `frontend/public/avatars/presenter.glb` only if validation passes.
6. **Failed export must not replace** a previously working runtime asset.

## What exists today vs next steps

| Capability | Status |
| --- | --- |
| Naming contracts (`contracts.py`) | Done |
| Rig / shape-key / clip validation | Done (`validate_rig.py`) |
| Headless GLB export | Done (`export_glb.py` → `exports/tmp/`) |
| Placeholder GLB (no Blender) | Done (`generate_placeholder_glb.py`; writes runtime directly for bootstrap) |
| Scene inspection script | Done (`inspect_scene.py`) |
| Shared paths / logging / backup helpers | Done (`common.py`) |
| Versioned `.blend` backups | Done (`save_versioned_blend` → `source/versions/`) |
| Temp export + export validation + promote | Done (`validate_export.py`, `promote_export.py`) |
| Targeted modify scripts (materials, etc.) | Planned |

### Shared helpers (`common.py`)

Future modify scripts should import these (via the same `_load_common()` pattern
as `inspect_scene.py` / `validate_rig.py` / `export_glb.py`):

| Helper | Purpose |
| --- | --- |
| `emit` / `report` | Prefixed log lines (`PASS:`, `ERROR:`, …) |
| `require_bpy` | Fail clearly when not running inside Blender |
| `load_scripts_module` | Load `contracts` (or other sibling modules) |
| `save_versioned_blend(label=...)` | Save + copy to `source/versions/` |
| `assert_export_path_allowed` | Block Blender export writes to the frontend runtime GLB |
| Path helpers | `tmp_presenter_glb`, `candidate_presenter_glb`, `runtime_presenter_glb`, … |

Backup files under `versions/` are gitignored (local recovery only).

## Commands available now

Run from the **repository root**. Requires Blender on PATH. Full presenter
commands also need `blender/source/presenter.blend`.

### Inspect scene (always run before modifying)

With a presenter file:

```bash
blender --background blender/source/presenter.blend --python blender/scripts/inspect_scene.py
```

Smoke-test without `presenter.blend` (uses Blender’s default startup; expect
`ERROR: No armature found` and exit code 1):

```bash
blender --background --python blender/scripts/inspect_scene.py
```

Output uses stable prefixes (`FILE:`, `OBJECT:`, `BONE:`, `SHAPE_KEY:`,
`ACTION:`, `RESULT:`, …) so an agent can parse the inventory. This script does
**not** score the naming contract — use `validate_rig.py` for that.

### Validate

```bash
blender --background blender/source/presenter.blend --python blender/scripts/validate_rig.py
```

### Export → validate → promote

Export to the **temporary** path (requires `presenter.blend`):

```bash
blender --background blender/source/presenter.blend --python blender/scripts/export_glb.py
```

Validate the temp GLB (plain Python, no Blender):

```bash
python blender/scripts/validate_export.py
```

Promote only if validation passes (copies temp → `blender/exports/presenter.glb`
and `frontend/public/avatars/presenter.glb`):

```bash
python blender/scripts/promote_export.py
```

You can also validate any GLB path:

```bash
python blender/scripts/validate_export.py frontend/public/avatars/presenter.glb
```

### Placeholder (Python only, no Blender)

Bootstrap shortcut — writes candidate + runtime directly (skips temp/promote):

```bash
python blender/scripts/generate_placeholder_glb.py
```

## Agent decision rule

| Kind of change | Preferred path |
| --- | --- |
| Gesture intensity, idle timing, camera, expression weights | JSON / TypeScript in `frontend/` |
| Suit color / simple materials | Prefer runtime material override; Blender only if baked into the asset |
| Bones, shape keys, topology, proportions, skin weights | Blender Python under `blender/scripts/` |
| Complex art-directed motion | Blender clip, or document a small manual Blender step |

Do not invent a full humanoid from primitives in Python. Start from a suitably
licensed base character, then automate inspection and targeted edits.
