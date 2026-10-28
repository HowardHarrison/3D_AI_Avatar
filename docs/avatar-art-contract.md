# Avatar art contract (stylized chatbot)

One-page contract for assets and look. Naming source of truth for validators remains [`blender/scripts/contracts.py`](../blender/scripts/contracts.py). Do not rename bones, clips, or shape keys casually — the runtime maps **semantic** names to these strings.

Related: [avatar-spec.md](avatar-spec.md) · [blender-pipeline.md](blender-pipeline.md) · [Overall_Architecture.md](Overall_Architecture.md)

---

## Product look

| Decision | Choice |
| --- | --- |
| Style | Stylized cartoon (Snapchat / Bitmoji-like), not photoreal |
| Why | Simple graphics stay intentional; avoids uncanny valley |
| Framing | Bust / upper body (`avatarConfig.camera`: closer shot on head/chest) |
| GLB role | Body: skeleton + skin weights + animation clips. Face: separate stylized mesh + morphs on `Head` |
| Three.js role | Materials, colors, accessories, outfit/skin presets; parents `face.glb` under `Head` |
| Stand-in body | `presenter.glb` — Mixamo-rigged (or placeholder) body; clay face morphs are **not** the long-term expression path |
| Stand-in face | `face.glb` from `generate_placeholder_face_glb.py` — drawn eyes/nose/mouth + contract morph names; root node `AvatarFace` |
| Mixamo note | Mixamo supplies **body + fingers**. Facial expressions come from the **face socket** GLB, not clay stretching on the body mesh |

---

## Skeleton (required bones)

Must exist with these exact names:

`Hips`, `Spine`, `Chest`, `Neck`, `Head`,  
`LeftShoulder`, `LeftUpperArm`, `LeftLowerArm`, `LeftHand`,  
`RightShoulder`, `RightUpperArm`, `RightLowerArm`, `RightHand`

### Optional body (legs / eyes)

See `OPTIONAL_BODY_BONES` in `contracts.py` (`LeftUpperLeg` … `RightFoot`, `LeftEye`, `RightEye`).

### Optional fingers (Mixamo path)

See `OPTIONAL_FINGER_BONES` in `contracts.py`. Naming is Mixamo-style without the `mixamorig:` prefix, three bones per digit:

`LeftHandThumb1..3`, `LeftHandIndex1..4`, `LeftHandMiddle1..3`, `LeftHandRing1..3`, `LeftHandPinky1..3`  
(and the same for `RightHand*`)

Rename map: [`blender/definitions/bone_rename_map.mixamo.json`](../blender/definitions/bone_rename_map.mixamo.json).

Some Mixamo downloads only include **index** fingers (plus tip `*Index4`). That is OK while fingers stay optional — validators warn on missing digits. Full hands need a Mixamo character exported with all fingers, or a different rig.

The box-head stand-in does **not** include fingers; validators emit a WARNING until a Mixamo-rigged character is promoted. Do not invent a second humanoid naming scheme per outfit — retarget onto this contract.

---

## Animation clips

### Required (current contract)

| Group | Exact clip names |
| --- | --- |
| Idle | `Idle_Neutral`, `Idle_Breathing` |
| Gestures | `Gesture_OpenHand`, `Gesture_Emphasize`, `Gesture_PointLeft`, `Gesture_PointRight`, `Gesture_HandsTogether` |
| Emotion (clips; optional if morphs cover it) | `Emotion_Neutral`, `Emotion_Serious`, `Emotion_Positive`, `Emotion_Concerned` |
| Blink | `Blink` |

Optional head / idle extras: `Head_Nod_Small`, `Head_Turn_*`, `Head_Tilt_*`, `Idle_ShiftWeight`, `Gesture_Nod` — see `OPTIONAL_ANIMATIONS` in `contracts.py`.

### Chatbot “talk” (behavior, not a new required clip yet)

For chat turns, **speaking** means:

1. Runtime state `SPEAKING` (already in the animation state machine), and  
2. Mouth / jaw morphs driven while TTS or test audio plays (`mouth_open`, `jaw_open`), and  
3. Optional gestures while talking.

A dedicated looping clip (e.g. `Talk_Loop`) is **Planned** — add it to `contracts.py` only when the asset and runtime are ready. Until then, do not break existing validators by requiring it.

---

## Face socket (Option 1)

Body and face are **two GLBs**:

| Piece | URL config | Root / attach |
| --- | --- | --- |
| Body | `avatarConfig.modelUrl` / `VITE_AVATAR_MODEL_URL` | Armature with required bones |
| Face | `avatarConfig.faceUrl` / `VITE_AVATAR_FACE_URL` | Node `AvatarFace` → parented to bone `Head` at runtime |

- Generate face: `python blender/scripts/generate_placeholder_face_glb.py` → `blender/exports/face.glb` + `frontend/public/avatars/face.glb`
- Runtime: `AvatarRuntime.attachFace` → `FacialController.retargetTo` binds the **face socket only** (never Mixamo body morphs)
- Replace `face.glb` with an authored head that **matches body art direction**; keep root `AvatarFace`

## Face pack (production expressions)

Expressions are **masks** mapped onto the face area and **crossfaded** (~200 ms). Do not stretch Mixamo body vertices for emotion.

| Semantic `ExpressionName` | Mask asset (required) |
| --- | --- |
| `neutral` | `/avatars/face/masks/neutral.webp` |
| `serious` | `/avatars/face/masks/serious.webp` |
| `positive` | `/avatars/face/masks/positive.webp` |
| `concerned` | `/avatars/face/masks/concerned.webp` |
| `amused` | `/avatars/face/masks/amused.webp` |
| `curious` | `/avatars/face/masks/curious.webp` |

- Source of truth in code: `frontend/src/services/avatar/facial/FacePackRegistry.ts`
- Asset drop folder: `frontend/public/avatars/face/masks/` (see README there)
- `setExpression(name)` resolves the mask id; UI never sees URLs or texture indexes
- **Mouth / speech** is a separate layer later (amplitude → visemes) — not full-face mask swaps per phoneme
- **Blink** stays its own layer (morph or overlay), not baked into every mask unless intentional
- Placeholder masks: `python blender/scripts/generate_face_pack_masks.py` → crossfaded on runtime `FaceCard` (`FaceMaskLayer`)
- Replace placeholder drawings with authored art that matches the body; keep filenames and 200 ms crossfade

`Emotion_*` body clips must not drive the held face (they wipe morphs). Gestures stay on the body skeleton.

## Facial morphs (shape keys)

**Body:** Mixamo clay morphs are **not** the expression path.  
**Face GLB:** morph names optional interim / mouth+blink layers. Preferred long-term emotion look = face-pack masks.

### Required exact names

`mouth_open`, `mouth_close`, `mouth_wide`, `mouth_round`, `mouth_smile`, `mouth_frown`,  
`jaw_open`, `brow_up`, `brow_down`,  
`eye_blink_left`, `eye_blink_right`, `eye_wide`, `eye_squint`

**Chat minimum in practice:** blinks + `mouth_open` / `jaw_open` + smile/frown for tone. The full required list stays so the placeholder and authored characters stay interchangeable.

### Optional (richer stylized expressions)

See `OPTIONAL_SHAPE_KEYS` in `contracts.py`:

`brow_inner_up`, `cheek_raise`, `mouth_left`, `mouth_right`, `nose_sneer`

These are **not** required on the stand-in. After a Mixamo import, add them in Blender (stubs first, then sculpt). Runtime presets `amused` and `curious` (plus enriched `positive` / `concerned`) use these optional keys when present. Mixamo will not create them for you.

---

## Skins and design (Three.js)

Allowed without re-exporting the whole character:

- Material color / roughness changes (skin, hair, shirt)
- Texture swaps on existing material slots
- Attach/detach accessory meshes that share the same skeleton

Requires Blender pipeline (validate → export → promote):

- New bone names, new morph names, or a different bind pose
- Body mesh topology that breaks existing skin weights

---

## Semantic API (unchanged rule)

UI and chat code use only semantic commands (`playGesture`, `setExpression`, `setHeadMotion`, `setGaze`, audio play/stop). Never clip indexes, bone paths, or raw `morphTargetInfluences` in React UI.

---

## Stand-in vs stylized character

| Asset | Status |
| --- | --- |
| `presenter.glb` (body) | **Keep** — Mixamo / stand-in body + clips |
| `face.glb` (face socket) | **Current Step 1** — placeholder stylized head on `Head` |
| Authored stylized face | **Next** — replace `face.glb`; same morph names + `AvatarFace` root |
| `presenter.blend` | Authoring source for body / clothing when replacing the stand-in |

When replacing either GLB: keep required bone / clip / shape-key names. Change meshes and materials; promote optional fingers when the body asset is ready.
