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
| `inspect_scene.py` | planned (not yet) |
| `validate_rig.py` | `blender/scripts/validate_rig.py` |
| `export_glb.py` | `blender/scripts/export_glb.py` |
| `validate_export.py` / promote | planned (not yet) |

## Prerequisites

- **Blender 3.6 LTS or 4.x** installed locally
- The `blender` executable available on your **PATH** so headless commands work
  from the repository root
- A source file at `blender/source/presenter.blend` for validate/export
  (optional until you adopt a real character; use the placeholder GLB for web
  work without Blender)

### Check Blender CLI

From the repository root:

```bash
blender --version
```

You should see a version line (3.6.x or 4.x). If the command is not found:

- **Windows:** add Blender’s install folder to PATH, or call the full path, e.g.
  `"C:\Program Files\Blender Foundation\Blender 4.2\blender.exe"`
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
2. **Backup before risky edits** — do not overwrite `presenter.blend` until the
   change is known-good; prefer a versioned copy under something like
   `blender/source/versions/` (folder to be added with the first modify script).
3. **Validate the scene** before export (`validate_rig.py`).
4. **Export to a temp path first** — never replace
   `frontend/public/avatars/presenter.glb` until export validation passes
   (temp export + promote scripts are planned; today export writes
   `blender/exports/presenter.glb` and you copy manually after checks).
5. **Failed export must not replace** a previously working runtime asset.

## What exists today vs next steps

| Capability | Status |
| --- | --- |
| Naming contracts (`contracts.py`) | Done |
| Rig / shape-key / clip validation | Done (`validate_rig.py`) |
| Headless GLB export | Done (`export_glb.py` → `exports/`) |
| Placeholder GLB (no Blender) | Done (`generate_placeholder_glb.py`) |
| Scene inspection script | Next learning step |
| Versioned `.blend` backups | Planned |
| Temp export + export validation + promote | Planned |
| Targeted modify scripts (materials, etc.) | Planned |

## Commands available now

Run from the **repository root**. Requires Blender and `presenter.blend` unless
noted.

Validate:

```bash
blender --background blender/source/presenter.blend --python blender/scripts/validate_rig.py
```

Export (writes `blender/exports/presenter.glb` today — treat as “candidate”
until you have visually checked the browser):

```bash
blender --background blender/source/presenter.blend --python blender/scripts/export_glb.py
```

Promote manually after you are satisfied:

`blender/exports/presenter.glb` → `frontend/public/avatars/presenter.glb`

Placeholder (Python only, no Blender):

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
