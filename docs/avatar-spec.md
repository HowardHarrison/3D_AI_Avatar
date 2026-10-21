# Avatar specification

Product direction: **stylized interactive chatbot** (Snapchat / Bitmoji-like), not photoreal news talent. Full art and naming contract: [avatar-art-contract.md](avatar-art-contract.md).

## Asset

- File: `frontend/public/avatars/presenter.glb`
- **Stand-in decision (Phase 0):** keep this GLB until a stylized chatbot character is authored. It must stay contract-compliant (`blender/scripts/contracts.py`).
- Humanoid armature with hips, spine, chest, neck, head, and arm chains
- Facial morph targets listed in [blender/README.md](../blender/README.md) and the art contract
- Default framing today: waist-up (camera at `[0, 1.65, 3.2]`, look at `[0, 1.4, 0]`, FOV 35). Chat UI may later prefer bust framing without changing bone names.

## Placeholder vs authored character

Until a stylized `blender/source/presenter.blend` (or successor) is exported, `blender/scripts/generate_placeholder_glb.py` / the current public GLB is the stand-in that **implements the naming contract** (clips, shape keys, bones). Replace meshes and materials for the cartoon look; do not change clip or shape-key names when you swap files.

## Look vs motion

| Concern | Owner |
| --- | --- |
| Bones, clips, morph **names** | Blender contract + GLB |
| Motion / expressions at runtime | `AvatarRuntime` (semantic API) |
| Skin colors, materials, accessories | Three.js / planned appearance layer |

## Runtime API

```ts
controller.playGesture("emphasize");
controller.setExpression("serious");
controller.setHeadMotion("nod");
controller.setGaze("camera");
controller.reset();
```

UI code must not read `morphTargetInfluences` or `animations[n]`.
