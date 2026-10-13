# Presenter source

Author `presenter.blend` in this folder. Until it exists, the web app can use the
generated placeholder GLB.

## Quick start (learning scaffold)

From the repository root:

```bash
blender --background --python blender/scripts/scaffold_presenter_blend.py -- --force
```

That writes a **non-production** contract-compliant stand-in. For the real
presenter, import a licensed humanoid and follow the adoption checklist in
[docs/blender-pipeline.md](../../docs/blender-pipeline.md).

`versions/` holds timestamped recoverable copies from `save_versioned_blend()`.
Those `.blend` backups are gitignored; only `.gitkeep` is tracked.

Do not commit secrets, scanned photos of real private individuals without rights, or huge texture packs into this directory.
