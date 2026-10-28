# Mixamo upload pack

## 1. Prepare the mesh (already done by script)

From the repository root:

```bash
blender --background blender/source/presenter.blend --python blender/scripts/export_mesh_for_mixamo.py --
```

This writes `presenter_mesh.fbx` in this folder.

## 2. Auto-rig on Mixamo (you do this in the browser)

1. Open [https://www.mixamo.com](https://www.mixamo.com) and sign in (Adobe account).
2. **Upload Character** → select `presenter_mesh.fbx`.
3. Use the **Auto-Rigger** (place markers on chin, wrists, elbows, knees, groin as prompted).
4. When rigged, optionally add a few animations, or download the T-pose character only.
5. **Download**:
   - Format: **FBX** or **GLB** (either works)
   - Skin: **With Skin**
   - Pose: **T-pose** is fine for the base; animations can be added later in our pipeline

## 3. Drop the file back into the repo

Save the download as exactly (gitignored):

```text
blender/exports/giga_chad_rigged.glb
```

or

```text
blender/exports/giga_chad_rigged.fbx
```

A copy may also live here as `giga_chad_rigged.fbx` while you work; the **canonical**
path for Step 3 import is under `blender/exports/` (not only this folder).

**Status (2026-10-28):** `blender/exports/giga_chad_rigged.fbx` is staged from a
prior Mixamo download. Re-run Mixamo only if you want a different character mesh;
otherwise proceed to Step 3 (import + rename).

## 4. Tell the agent (or run yourself)

```bash
blender --background --python blender/scripts/import_base_glb.py -- --input blender/exports/giga_chad_rigged.glb
blender --background blender/source/presenter.blend --python blender/scripts/apply_rename_map.py -- --map blender/definitions/bone_rename_map.mixamo.json --dry-run
# fix armature name in the JSON if dry-run says Armature not found
blender --background blender/source/presenter.blend --python blender/scripts/apply_rename_map.py -- --map blender/definitions/bone_rename_map.mixamo.json
blender --background blender/source/presenter.blend --python blender/scripts/create_animation.py -- --create-all-required
cd frontend
npm run avatar:release
npm run dev
```

**Fingers:** Mixamo usually includes finger bones. After import, rename with
`blender/definitions/bone_rename_map.mixamo.json` (maps into
`OPTIONAL_FINGER_BONES` in `contracts.py`). The stand-in avatar does not have
fingers; that is expected until you promote a Mixamo-rigged character.

**Face:** Mixamo usually has **no** facial morphs. After rename, add
`REQUIRED_SHAPE_KEYS` (and later `OPTIONAL_SHAPE_KEYS`: `brow_inner_up`,
`cheek_raise`, `mouth_left`, `mouth_right`, `nose_sneer`) in Blender — e.g.
`add_stub_shape_keys.py` then sculpt. Expressions stay incomplete until then.

