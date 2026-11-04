# Mixamo upload pack

## 1. Prepare the mesh

**From an external T-pose FBX** (e.g. Hunyuan / AI mesh at repo root):

```bash
blender --background --python blender/scripts/prepare_fbx_for_mixamo.py -- --input ai_boy_tpose.fbx
```

This cleans the mesh (strip leftover rigging, join, merge verts, normals, feet origin),
decimates dense AI meshes to ~80k faces for Mixamo, and writes e.g.
`ai_boy_tpose_mesh.fbx` in this folder.

**From the existing `presenter.blend`:**

```bash
blender --background blender/source/presenter.blend --python blender/scripts/export_mesh_for_mixamo.py --
```

That writes `presenter_mesh.fbx` in this folder.

## 2. Auto-rig on Mixamo (you do this in the browser)

1. Open [https://www.mixamo.com](https://www.mixamo.com) and sign in (Adobe account).
2. **Upload Character** → select `presenter_mesh.fbx`.
3. Use the **Auto-Rigger** (place markers on chin, wrists, elbows, knees, groin as prompted).
4. When rigged, optionally add a few animations, or download the T-pose character only.
5. **Download**:
   - Format: **FBX** or **GLB** (either works)
   - Skin: **With Skin**
   - Pose: **T-pose** is fine for the base; animations can be added later in our pipeline

## 3. Drop the Mixamo download + restore textures (Option A)

Save the Mixamo download (With Skin) somewhere reachable, e.g. repo root:

```text
ai_boy_tpose_mesh.fbx          # Mixamo rigged (gray)
ai_boy_tpose_texture.fbx       # original high-res with PBR maps
```

**Preferred (exact textures):** transfer the Mixamo rig onto the original
textured mesh (keeps Hunyuan UVs/maps — do not bake onto Mixamo UVs):

```bash
blender --background --python blender/scripts/transfer_rig_to_textured.py -- ^
  --rigged ai_boy_tpose_mesh.fbx --textured ai_boy_tpose_texture.fbx
```

Output: `blender/exports/ai_boy_rigged_textured.glb`

(Alternative / older: `bake_textures_onto_rigged.py` rebakes onto Mixamo UVs and
often scrambles face/clothes colors — avoid unless you need that path.)

Then copy/rename for the import step:

```text
blender/exports/giga_chad_rigged.glb
```

(or `.fbx` if you skip baking and import the gray Mixamo file directly)

**Status (2026-11-04):** Bake path is available via `bake_textures_onto_rigged.py`.
Use the textured GLB for import when you want color in the web app.

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

