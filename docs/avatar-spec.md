# Avatar specification

## Asset

- File: `apps/web/public/avatars/presenter.glb`
- Humanoid armature with hips, spine, chest, neck, head, and arm chains
- Facial morph targets listed in [blender/README.md](../blender/README.md)
- Default framing: waist-up (camera at `[0, 1.65, 3.2]`, look at `[0, 1.4, 0]`, FOV 35)

## Placeholder vs authored character

Until `blender/source/presenter.blend` exists, `blender/scripts/generate_placeholder_glb.py` writes a low-poly stand-in that **implements the naming contract** (clips, shape keys, bones). Replace it with a Blender export for a professional look. Do not change clip or shape-key names when you swap files.

## Runtime API

```ts
controller.playGesture("emphasize");
controller.setExpression("serious");
controller.setHeadMotion("nod");
controller.setGaze("camera");
controller.reset();
```

UI code must not read `morphTargetInfluences` or `animations[n]`.
