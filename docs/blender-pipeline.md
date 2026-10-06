# Blender pipeline

Full authoring notes: [blender/README.md](../blender/README.md)

## Commands

Validate (requires Blender and `presenter.blend`):

```bash
blender --background blender/source/presenter.blend --python blender/scripts/validate_rig.py
```

Export:

```bash
blender --background blender/source/presenter.blend --python blender/scripts/export_glb.py
```

Placeholder GLB (no Blender):

```bash
python blender/scripts/generate_placeholder_glb.py
```

Copy `blender/exports/presenter.glb` to `frontend/public/avatars/presenter.glb`.

The web application never loads `.blend` files.
