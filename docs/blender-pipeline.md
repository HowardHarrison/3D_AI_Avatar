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
| `modify_materials.py` | `blender/scripts/modify_materials.py` |
| `modify_character.py` | `blender/scripts/modify_character.py` |
| `create_animation.py` | `blender/scripts/create_animation.py` |
| `scaffold_presenter_blend.py` | `blender/scripts/scaffold_presenter_blend.py` |
| `apply_rename_map.py` | `blender/scripts/apply_rename_map.py` |
| `import_base_glb.py` | `blender/scripts/import_base_glb.py` |

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
| Targeted material modify | Done (`modify_materials.py`) |
| Targeted character modify (safe ops) | Done (`modify_character.py`) |
| Stub animation create | Done (`create_animation.py`) |
| Learning `.blend` scaffold | Done (`scaffold_presenter_blend.py`) |
| Bone rename map for licensed imports | Done (`apply_rename_map.py` + example JSON) |
| npm script glue + suit-color example | Done (`frontend/package.json` `avatar:*` scripts) |

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

### Modify a material (first edit script)

List materials in the open `.blend`:

```bash
blender --background blender/source/presenter.blend --python blender/scripts/modify_materials.py -- --list
```

Change one material base color (RGB floats 0–1). This backs up under
`source/versions/`, saves the blend, runs `validate_rig`, and exports to
`exports/tmp/`:

```bash
blender --background blender/source/presenter.blend --python blender/scripts/modify_materials.py -- --material Suit --color 0.05,0.15,0.45
```

Then validate and promote the temp GLB as usual. Prefer a runtime material
override in the frontend when you do not need the color baked into the asset.

Smoke-test without a saved `.blend` (default Cube scene):

```bash
blender --background --python blender/scripts/modify_materials.py -- --list
blender --background --python blender/scripts/modify_materials.py -- --material Material --color 1,0,0 --no-backup --skip-validate --skip-export
```

### Modify character (safe transforms only)

Does **not** remesh, re-weight, or sculpt. One operation per run.

List mesh/armature objects (and bones):

```bash
blender --background blender/source/presenter.blend --python blender/scripts/modify_character.py -- --list
```

Examples:

```bash
blender --background blender/source/presenter.blend --python blender/scripts/modify_character.py -- --object Armature --apply-transforms
blender --background blender/source/presenter.blend --python blender/scripts/modify_character.py -- --object Armature --scale 1,1,1
blender --background blender/source/presenter.blend --python blender/scripts/modify_character.py -- --object OldBody --rename PresenterBody
blender --background blender/source/presenter.blend --python blender/scripts/modify_character.py -- --armature Armature --rename-bone mixamorig:Hips=Hips
```

Smoke-test:

```bash
blender --background --python blender/scripts/modify_character.py -- --list
blender --background --python blender/scripts/modify_character.py -- --object Cube --scale 1.1,1.1,1.1 --no-backup --skip-validate --skip-export
```

### Create stub animations (Step 7)

Prefer JSON / TypeScript for simple procedural motion. Use Blender clips when the
GLB must contain a contract-named action.

```bash
blender --background blender/source/presenter.blend --python blender/scripts/create_animation.py -- --list
blender --background blender/source/presenter.blend --python blender/scripts/create_animation.py -- --create Idle_Breathing
blender --background blender/source/presenter.blend --python blender/scripts/create_animation.py -- --create-all-required
```

Stubs are teaching motions, not art-directed performance.

### Scaffold or adopt a character (Step 8)

**Option A — learning scaffold (not a production presenter)**

Creates `blender/source/presenter.blend` with required bones, shape-key names,
materials, and stub clips so the pipeline can be tested end-to-end:

```bash
blender --background --python blender/scripts/scaffold_presenter_blend.py -- --force
python blender/scripts/validate_export.py
python blender/scripts/promote_export.py
```

**Option B — licensed base character (recommended for the real avatar)**

The character must be **rigged** (armature + skin). A static mesh cannot gesture.

### Mixamo path (giga_chad / similar)

Mixamo auto-rigging is done in the browser (Adobe login). The repo prepares the
upload mesh and finishes import → rename → release after you drop the rigged file.

1. Export upload FBX from the current `presenter.blend` mesh:

```bash
blender --background blender/source/presenter.blend --python blender/scripts/export_mesh_for_mixamo.py --
```

2. Follow [blender/exports/mixamo_upload/README.md](../blender/exports/mixamo_upload/README.md):
   upload → Auto-Rigger → download **With Skin** as
   `blender/exports/giga_chad_rigged.glb` (or `.fbx`).

3. Re-import into Blender source:

```bash
blender --background --python blender/scripts/import_base_glb.py -- --input blender/exports/giga_chad_rigged.glb
```

4. Rename Mixamo bones toward `contracts.py` (body + **fingers** via
   `OPTIONAL_FINGER_BONES` in the Mixamo rename map):

```bash
blender --background blender/source/presenter.blend --python blender/scripts/apply_rename_map.py -- --map blender/definitions/bone_rename_map.mixamo.json --dry-run
blender --background blender/source/presenter.blend --python blender/scripts/apply_rename_map.py -- --map blender/definitions/bone_rename_map.mixamo.json
```

If dry-run says the armature name is wrong, edit `"armature"` in the JSON (check
`inspect_scene.py` output).

5. Mixamo usually has **no** facial morphs (required or optional) and only a
   generic action name. Add stub shape keys + contract clips before release.
   Optional richer keys (`OPTIONAL_SHAPE_KEYS`: brow_inner_up, cheek_raise, …)
   come later — see [avatar-art-contract.md](avatar-art-contract.md).

```bash
blender --background blender/source/presenter.blend --python blender/scripts/add_stub_shape_keys.py --
blender --background blender/source/presenter.blend --python blender/scripts/create_animation.py -- --create-all-required
```

6. From `frontend/`:

```bash
npm run avatar:release
npm run dev
```

Stub shape keys satisfy the naming contract only — they are not art-directed
expressions. Replace them later with real morphs if needed.

Do not claim production character quality while only the scaffold or unrigged mesh is in use.

### Placeholder GLB (Python only, no Blender)

Bootstrap shortcut — writes candidate + runtime directly (skips temp/promote):

```bash
python blender/scripts/generate_placeholder_glb.py
```

### npm script glue (from `frontend/`)

Requires Blender on PATH for inspect / validate-rig / export / scaffold.
Python-only scripts work without Blender.

| npm script | What it runs |
| --- | --- |
| `npm run avatar:inspect` | `inspect_scene.py` on `presenter.blend` |
| `npm run avatar:validate-rig` | `validate_rig.py` |
| `npm run avatar:export` | `export_glb.py` → `exports/tmp/` |
| `npm run avatar:validate-export` | `validate_export.py` |
| `npm run avatar:promote` | `promote_export.py` |
| `npm run avatar:release` | export → validate-export → promote |
| `npm run avatar:scaffold` | regenerate learning `presenter.blend` |
| `npm run generate:avatar` | placeholder GLB (no Blender) |

### Example: change suit color

Bake a new suit color into the asset (scaffold material is named `Suit`). Prefer a
frontend material override when you do not need the color in the GLB.

From the **repository root** (Blender flags go after `--`):

```bash
# 1) Inspect material names
blender --background blender/source/presenter.blend --python blender/scripts/modify_materials.py -- --list

# 2) Change Suit base color (backs up, validates rig, exports temp GLB)
blender --background blender/source/presenter.blend --python blender/scripts/modify_materials.py -- --material Suit --color 0.02,0.08,0.25
```

From **`frontend/`** (promote the temp export into the web app):

```bash
npm run avatar:validate-export
npm run avatar:promote
npm run dev
```

Or in one shot after the material script already exported to tmp:

```bash
npm run avatar:validate-export && npm run avatar:promote && npm run dev
```

If you only changed the `.blend` and still need export:

```bash
npm run avatar:release
npm run dev
```

Confirm in the browser that the presenter suit looks darker blue. Restore from
`blender/source/versions/` if you need to undo the `.blend` edit.

## Agent decision rule

| Kind of change | Preferred path |
| --- | --- |
| Gesture intensity, idle timing, camera, expression weights | JSON / TypeScript in `frontend/` |
| Suit color / simple materials | Prefer runtime material override; Blender only if baked into the asset |
| Bones, shape keys, topology, proportions, skin weights | Blender Python under `blender/scripts/` |
| Complex art-directed motion | Blender clip, or document a small manual Blender step |

Do not invent a full humanoid from primitives in Python. Start from a suitably
licensed base character, then automate inspection and targeted edits.
