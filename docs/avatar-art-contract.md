# Avatar art contract (stylized chatbot)

One-page contract for assets and look. Naming source of truth for validators remains [`blender/scripts/contracts.py`](../blender/scripts/contracts.py). Do not rename bones, clips, or shape keys casually — the runtime maps **semantic** names to these strings.

Related: [avatar-spec.md](avatar-spec.md) · [blender-pipeline.md](blender-pipeline.md) · [Overall_Architecture.md](Overall_Architecture.md)

---

## Product look

| Decision | Choice |
| --- | --- |
| Style | Stylized cartoon (Snapchat / Bitmoji-like), not photoreal |
| Why | Simple graphics stay intentional; avoids uncanny valley |
| Framing | Bust / upper body for chat (waist-up camera is fine until reframed) |
| GLB role | Skeleton + skin weights + animation clips (+ facial morphs) |
| Three.js role | Materials, colors, accessories, outfit/skin presets at runtime |
| Temporary asset | Keep `frontend/public/avatars/presenter.glb` as the **stand-in** until a stylized rig is authored (Phase 1 art step) |

---

## Skeleton (required bones)

Must exist with these exact names:

`Hips`, `Spine`, `Chest`, `Neck`, `Head`,  
`LeftShoulder`, `LeftUpperArm`, `LeftLowerArm`, `LeftHand`,  
`RightShoulder`, `RightUpperArm`, `RightLowerArm`, `RightHand`

Optional (legs / eyes): see `OPTIONAL_BONES` in `contracts.py`.

All swappable looks must bind to this bone set (or be retargeted onto it). Do not invent a second humanoid naming scheme per outfit.

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

Required exact names:

`mouth_open`, `mouth_close`, `mouth_wide`, `mouth_round`, `mouth_smile`, `mouth_frown`,  
`jaw_open`, `brow_up`, `brow_down`,  
`eye_blink_left`, `eye_blink_right`, `eye_wide`, `eye_squint`

**Chat minimum in practice:** blinks + `mouth_open` / `jaw_open` + smile/frown for tone. The full list stays required so the placeholder and authored characters stay interchangeable.

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
| Stylized chatbot character | **Next art step (Phase 1)** — same names, cartoon proportions, flat/soft materials |
| `presenter.blend` | Authoring source when replacing the stand-in |

When replacing the GLB: same bone / clip / shape-key names. Change meshes and materials, not the contract.
