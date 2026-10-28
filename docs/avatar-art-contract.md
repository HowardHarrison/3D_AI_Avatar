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
| GLB role | Skeleton + skin weights + animation clips (+ facial morphs) |
| Three.js role | Materials, colors, accessories, outfit/skin presets at runtime |
| Stand-in asset | `presenter.glb` from `generate_placeholder_glb.py` — stylized big-head boxes with drawn eyes (white+pupil), nose, and mouth; replace later with Mixamo-rigged stylized character, same bone/clip names |
| Mixamo note | Mixamo supplies **body + fingers**. It usually supplies **no facial morphs** — add shape keys in Blender after import |

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

`LeftHandThumb1..3`, `LeftHandIndex1..3`, `LeftHandMiddle1..3`, `LeftHandRing1..3`, `LeftHandPinky1..3`  
(and the same for `RightHand*`)

Rename map: [`blender/definitions/bone_rename_map.mixamo.json`](../blender/definitions/bone_rename_map.mixamo.json).

The box-head stand-in does **not** include fingers; validators emit a single WARNING until a Mixamo-rigged character is promoted. Do not invent a second humanoid naming scheme per outfit — retarget onto this contract.

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

## Facial morphs (shape keys)

### Required exact names

`mouth_open`, `mouth_close`, `mouth_wide`, `mouth_round`, `mouth_smile`, `mouth_frown`,  
`jaw_open`, `brow_up`, `brow_down`,  
`eye_blink_left`, `eye_blink_right`, `eye_wide`, `eye_squint`

**Chat minimum in practice:** blinks + `mouth_open` / `jaw_open` + smile/frown for tone. The full required list stays so the placeholder and authored characters stay interchangeable.

### Optional (richer stylized expressions)

See `OPTIONAL_SHAPE_KEYS` in `contracts.py`:

`brow_inner_up`, `cheek_raise`, `mouth_left`, `mouth_right`, `nose_sneer`

These are **not** required on the stand-in. After a Mixamo import, add them in Blender (stubs first, then sculpt) before expanding runtime `ExpressionName` presets. Mixamo will not create them for you.

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
| `presenter.glb` (current) | **Keep** — contract-compliant stand-in for runtime work |
| Stylized chatbot character | **Next** — Mixamo-rigged cartoon mesh + Blender face morphs; same required names; optional fingers + optional face keys |
| `presenter.blend` | Authoring source when replacing the stand-in |

When replacing the GLB: keep required bone / clip / shape-key names. Change meshes and materials; promote optional fingers and optional face keys when the new asset is ready.
