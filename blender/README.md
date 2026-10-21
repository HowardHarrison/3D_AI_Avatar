# Blender avatar pipeline

Blender authors the **stylized** chatbot avatar (skeleton, clips, morphs). The browser never opens `.blend` files.
The only runtime asset is `presenter.glb` (stand-in until a cartoon character is exported). Naming contract: [docs/avatar-art-contract.md](../docs/avatar-art-contract.md).

Safe inspect → modify → validate → export → promote flow, CLI prerequisites,
and path mapping: [docs/blender-pipeline.md](../docs/blender-pipeline.md).

From `frontend/` you can also run `npm run avatar:inspect`, `avatar:validate-rig`,
`avatar:export`, `avatar:validate-export`, `avatar:promote`, `avatar:release`,
and `avatar:scaffold` (Blender must be on PATH for the Blender-backed commands).

## Goal

A lightweight **stylized** humanoid, framed **waist-up / bust**, suitable for chat,
education, and a future conversational assistant.

Target hardware is modest (integrated GPU / 2 GB discrete). Prefer:

- low-to-medium polygon body
- 1K textures or smaller
- no ray tracing, 4K maps, or dense hair cards

## Prerequisites

- Blender **3.6 LTS, 4.x, or 5.x**
- `blender` on your **PATH** (see [docs/blender-pipeline.md](../docs/blender-pipeline.md)
  for Windows full-path examples)

Check:

```bash
blender --version
```

## Folder layout

Automation lives in **`scripts/`** (not `automation/`). MVP docs that say
`blender/automation/` mean this folder.

| Path | Purpose |
| --- | --- |
| `source/presenter.blend` | Authoring file (you create this) |
| `source/versions/` | Timestamped `.blend` backups (`save_versioned_blend`; gitignored) |
| `animations/` | Optional clip library notes or linked actions |
| `exports/tmp/presenter.glb` | Unvalidated headless export (gitignored) |
| `exports/presenter.glb` | Validated candidate after promote |
| `scripts/common.py` | Paths, logging, backup, safe-export guards |
| `scripts/contracts.py` | Shared bone / shape-key / clip names |
| `scripts/inspect_scene.py` | Inventory objects, bones, keys, clips (no contract scoring) |
| `scripts/validate_rig.py` | PASS / WARNING / ERROR checks on the `.blend` |
| `scripts/export_glb.py` | Headless export → `exports/tmp/` only |
| `scripts/validate_export.py` | Validate temp GLB (plain Python) |
| `scripts/promote_export.py` | Copy temp → candidate + frontend runtime |
| `scripts/modify_materials.py` | List / change one material base color (backup + validate + temp export) |
| `scripts/modify_character.py` | Safe character ops: scale, apply transforms, rename object/bone |
| `scripts/create_animation.py` | Create contract-named stub Action clips |
| `scripts/scaffold_presenter_blend.py` | Learning `presenter.blend` (not production) |
| `scripts/apply_rename_map.py` | Batch bone renames from JSON map |
| `scripts/import_base_glb.py` | Import an external `.glb`/`.fbx` into `source/presenter.blend` |
| `scripts/add_stub_shape_keys.py` | Add contract facial shape-key *names* (Mixamo has none) |
| `scripts/improve_facial_shape_keys.py` | Rebuild visible head-region morphs for expressions |
| `definitions/bone_rename_map.example.json` | Example Mixamo-style rename map |
| `scripts/generate_placeholder_glb.py` | Bootstrap GLB (writes runtime directly) |

## Naming contract

Use **these exact animation names** (never rely on clip index):

- Idle: `Idle_Neutral`, `Idle_Breathing`, `Idle_ShiftWeight` (optional)
- Head: `Head_Nod_Small`, `Head_Turn_Left`, `Head_Turn_Right`, `Head_Tilt_Left`, `Head_Tilt_Right`
- Gestures (at least five): `Gesture_OpenHand`, `Gesture_Emphasize`, `Gesture_PointLeft`, `Gesture_PointRight`, `Gesture_HandsTogether`
- Emotion clips (optional if shape keys cover expressions): `Emotion_Neutral`, `Emotion_Serious`, `Emotion_Positive`, `Emotion_Concerned`
- `Blink`

Required facial shape keys / morph targets:

`mouth_open`, `mouth_close`, `mouth_wide`, `mouth_round`, `mouth_smile`, `mouth_frown`, `jaw_open`, `brow_up`, `brow_down`, `eye_blink_left`, `eye_blink_right`, `eye_wide`, `eye_squint`

Required bones (humanoid): `Hips`, `Spine`, `Chest`, `Neck`, `Head`, plus shoulder/arm/hand chains on both sides.

## Local workflow

For structural changes, follow the **safe sequence** in
[docs/blender-pipeline.md](../docs/blender-pipeline.md) (inspect → modify →
backup → validate rig → export tmp → validate export → promote).

1. Author `source/presenter.blend` (applied transforms, Y-up or Blender default then correct on export).
2. Inspect (from repo root) — always before modifying:

```bash
blender --background blender/source/presenter.blend --python blender/scripts/inspect_scene.py
```

3. Validate the `.blend` contract:

```bash
blender --background blender/source/presenter.blend --python blender/scripts/validate_rig.py
```

4. Export to the temporary path:

```bash
blender --background blender/source/presenter.blend --python blender/scripts/export_glb.py
```

5. Validate the temp GLB, then promote to candidate + runtime:

```bash
python blender/scripts/validate_export.py
python blender/scripts/promote_export.py
```

Optional — change a baked material color (inspect names first with `--list`):

```bash
blender --background blender/source/presenter.blend --python blender/scripts/modify_materials.py -- --list
blender --background blender/source/presenter.blend --python blender/scripts/modify_materials.py -- --material Suit --color 0.05,0.15,0.45
```

Optional — safe character transforms / renames (not remesh):

```bash
blender --background blender/source/presenter.blend --python blender/scripts/modify_character.py -- --list
blender --background blender/source/presenter.blend --python blender/scripts/modify_character.py -- --object Armature --apply-transforms
```

Until your character is ready, generate the placeholder:

```bash
python blender/scripts/generate_placeholder_glb.py
```

Then copy the export into `frontend/public/avatars/presenter.glb`.

## Export settings (manual)

- Format: glTF Binary (`.glb`)
- Include: meshes, materials, textures, armatures, shape keys, animations
- Apply modifiers
- +Y up (glTF)
- Do not need Draco unless file size becomes a problem

## Orientation and scale

- Character standing on the origin, facing +Z in glTF (Blender -Y forward / +Z up typically converts correctly with the official exporter)
- Real-world metres: eye height near 1.6 m so the default camera `[0, 1.65, 3.2]` frames waist-up
- Apply location/rotation/scale on meshes before export
