# Blender presenter pipeline

Blender authors the 3D news presenter. The browser never opens `.blend` files.
The only runtime asset is `presenter.glb`.

## Goal

A lightweight professional humanoid, framed **waist-up**, suitable for news,
education, and a future conversational assistant.

Target hardware is modest (integrated GPU / 2 GB discrete). Prefer:

- low-to-medium polygon body
- 1K textures or smaller
- no ray tracing, 4K maps, or dense hair cards

## Folder layout

| Path | Purpose |
| --- | --- |
| `source/presenter.blend` | Authoring file (you create this) |
| `animations/` | Optional clip library notes or linked actions |
| `exports/presenter.glb` | Headless export output |
| `scripts/validate_rig.py` | PASS / WARNING / ERROR checks |
| `scripts/export_glb.py` | Headless glTF Binary export |
| `scripts/generate_placeholder_glb.py` | Temporary contract-compliant GLB for web development |

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

1. Author `source/presenter.blend` (applied transforms, Y-up or Blender default then correct on export).
2. Validate:

```bash
blender --background blender/source/presenter.blend --python blender/scripts/validate_rig.py
```

3. Export:

```bash
blender --background blender/source/presenter.blend --python blender/scripts/export_glb.py
```

4. Copy `blender/exports/presenter.glb` to `frontend/public/avatars/presenter.glb`.

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
