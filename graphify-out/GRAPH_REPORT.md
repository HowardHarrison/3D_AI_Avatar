# Graph Report - AI_3D_Avatar  (2026-10-19)

## Corpus Check
- cluster-only mode — file stats not available

## Summary
- 578 nodes · 957 edges · 23 communities (21 shown, 2 thin omitted)
- Extraction: 99% EXTRACTED · 1% INFERRED · 0% AMBIGUOUS · INFERRED: 6 edges (avg confidence: 0.8)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `f912de9b`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- AvatarScene.tsx
- AvatarRuntime.ts
- AvatarRuntime
- common.py
- GltfBuilder
- create_animation.py
- package.json
- modify_character.py
- AudioController
- import_base_glb
- modify_materials.py
- scripts
- _improve_impl
- compilerOptions
- scaffold_presenter_blend.py
- add_stub_shape_keys.py
- Load ``common.py`` from the same scripts directory (works inside Blender).
- export_mesh_for_mixamo.py
- main
- export_glb.py
- validate_rig.py
- .prettierrc.json
- vite-env.d.ts

## God Nodes (most connected - your core abstractions)
1. `AvatarRuntime` - 26 edges
2. `scripts` - 19 edges
3. `AvatarController` - 16 edges
4. `AnimationController` - 16 edges
5. `compilerOptions` - 16 edges
6. `modify_character()` - 15 edges
7. `ExpressionName` - 14 edges
8. `FacialController` - 14 edges
9. `GltfBuilder` - 14 edges
10. `AudioController` - 14 edges

## Surprising Connections (you probably didn't know these)
- `AnimationControlsProps` --references--> `AvatarHandle`  [EXTRACTED]
  frontend/src/features/avatar/components/AnimationControls.tsx → frontend/src/features/avatar/types.ts
- `AvatarSceneProps` --inherits--> `AvatarLoadHandlers`  [EXTRACTED]
  frontend/src/features/avatar/components/AvatarScene.tsx → frontend/src/features/avatar/types.ts
- `DebugPanelProps` --references--> `AvatarHandle`  [EXTRACTED]
  frontend/src/features/avatar/components/DebugPanel.tsx → frontend/src/features/avatar/types.ts
- `FacialController` --references--> `ExpressionName`  [EXTRACTED]
  frontend/src/services/avatar/facial/FacialController.ts → frontend/src/types/animation.ts
- `AvatarRuntime` --implements--> `AvatarController`  [EXTRACTED]
  frontend/src/services/avatar/AvatarRuntime.ts → frontend/src/types/avatar.ts

## Import Cycles
- None detected.

## Communities (23 total, 2 thin omitted)

### Community 0 - "AvatarScene.tsx"
Cohesion: 0.06
Nodes (42): App(), StatusPanel(), StatusPanelProps, avatarConfig, defaultExpression, defaultGaze, SemanticExpression, SemanticGesture (+34 more)

### Community 1 - "AvatarRuntime.ts"
Cohesion: 0.07
Nodes (31): animationRegistry, EXPRESSION_NAMES, GESTURE_NAMES, HEAD_NAMES, isExpressionName(), isGestureName(), isHeadMotionName(), resolveExpressionClip() (+23 more)

### Community 2 - "AvatarRuntime"
Cohesion: 0.06
Nodes (10): AnimationController, ALLOWED, AnimationStateMachine, ResolvedClip, IdleController, randomBetween(), AvatarRuntime, FacialController (+2 more)

### Community 3 - "common.py"
Cohesion: 0.07
Nodes (50): assert_export_path_allowed(), blender_dir(), candidate_presenter_glb(), emit(), exports_dir(), exports_tmp_dir(), load_scripts_module(), presenter_blend_path() (+42 more)

### Community 4 - "GltfBuilder"
Cohesion: 0.06
Nodes (30): Shared naming contracts for Blender validation, GLB export, and the placeholder…, _align4(), _box_indices(), _box_normals(), _box_positions(), build_presenter(), GltfBuilder, _identity_mat4() (+22 more)

### Community 5 - "create_animation.py"
Cohesion: 0.07
Nodes (41): _action_fcurve_count(), _allowed_clip_names(), _assign_nla_slot(), _bone_exists(), _build_bone_clip(), key_loc(), key_rot(), need() (+33 more)

### Community 6 - "package.json"
Cohesion: 0.05
Nodes (39): dependencies, react, react-dom, @react-three/drei, @react-three/fiber, three, devDependencies, eslint (+31 more)

### Community 7 - "modify_character.py"
Cohesion: 0.10
Nodes (29): _apply_transforms(), _build_parser(), _count_ops(), _fmt_vec(), _list_objects(), modify_character(), _parse_bone_rename(), _parse_vec3() (+21 more)

### Community 9 - "import_base_glb"
Cohesion: 0.15
Nodes (17): apply_rename_map(), _load_common(), Apply a JSON bone rename map toward the avatar naming contract. Use after…, Rename bones from a JSON map; return process exit code., _script_argv(), _backup_existing_blend(), _clear_scene(), import_base_glb() (+9 more)

### Community 10 - "modify_materials.py"
Cohesion: 0.17
Nodes (18): _build_parser(), _list_materials(), _load_common(), _material_has_nodes(), modify_materials(), _parse_color(), ArgumentParser, Change one material base color in the open .blend (targeted, reversible edit).… (+10 more)

### Community 11 - "scripts"
Cohesion: 0.11
Nodes (19): scripts, avatar:export, avatar:export-mixamo, avatar:import-rigged, avatar:inspect, avatar:promote, avatar:release, avatar:scaffold (+11 more)

### Community 12 - "_improve_impl"
Cohesion: 0.14
Nodes (15): _apply_deltas(), _find_armature(), _head_vertex_data(), improve_facial_shape_keys(), _improve_impl(), _pick_mesh(), Rebuild contract facial shape keys with visible head-region deformations.…, Clear shape keys and recreate Basis + required empty keys. (+7 more)

### Community 13 - "compilerOptions"
Cohesion: 0.11
Nodes (17): compilerOptions, allowImportingTsExtensions, isolatedModules, jsx, lib, module, moduleDetection, moduleResolution (+9 more)

### Community 14 - "scaffold_presenter_blend.py"
Cohesion: 0.21
Nodes (13): _add_bone(), _build_armature(), _build_meshes(), _clear_scene(), _load_common(), Create a contract-compliant learning scaffold at…, Create simple body + head meshes with required shape keys., Build and save the learning presenter.blend; return exit code. (+5 more)

### Community 15 - "add_stub_shape_keys.py"
Cohesion: 0.27
Nodes (9): add_stub_shape_keys(), _load_common(), _pick_mesh(), Add contract-named facial shape keys (tiny stubs) to the presenter mesh. Mixamo…, Return script flags after ``--``, or plain-python argv; ignore Blender flags., Return the mesh object to receive shape keys., Create missing required shape keys on the presenter mesh., _script_argv() (+1 more)

### Community 16 - "Load ``common.py`` from the same scripts directory (works inside Blender)."
Cohesion: 0.29
Nodes (7): Load ``common.py`` from the same scripts directory (works inside Blender)., _load_common(), inspect_scene(), _load_common(), Inventory the open Blender scene for AI-agent and developer inspection. Prints…, Walk the open .blend and print an inventory; return process exit code., _load_common()

### Community 17 - "export_mesh_for_mixamo.py"
Cohesion: 0.36
Nodes (7): export_mesh_for_mixamo(), _load_common(), _pick_mesh(), Export the presenter mesh as FBX for Mixamo (or similar) auto-rigging. Mixamo…, Prefer a mesh named Man / Presenter*; else the largest mesh by vertex count., Export a Mixamo-upload FBX from the open blend; return exit code., _script_argv()

### Community 18 - "main"
Cohesion: 0.38
Nodes (6): main(), Path, Write a short royalty-free presenter test tone as MP3 (or WAV fallback). python…, Write a simple A4 tone with a short fade so it is pleasant for debug playback., Create public/audio/test-presenter.mp3 when ffmpeg is available, else WAV., _write_wav()

### Community 19 - "export_glb.py"
Cohesion: 0.50
Nodes (4): export(), _load_common(), Export presenter.blend to blender/exports/tmp/presenter.glb (unvalidated).…, Export the current Blender scene as a temporary GLB under exports/tmp/.

### Community 20 - "validate_rig.py"
Cohesion: 0.50
Nodes (4): _load_common(), Validate presenter.blend against the Phase 1 avatar contract. Run inside…, Inspect the open Blender file and return the process exit code., validate()

### Community 21 - ".prettierrc.json"
Cohesion: 0.40
Nodes (4): printWidth, semi, singleQuote, trailingComma

## Knowledge Gaps
- **97 isolated node(s):** `StatusPanelProps`, `SemanticExpression`, `SemanticGesture`, `SemanticHeadMotion`, `AppEnvironment` (+92 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 274 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **2 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Load ``common.py`` from the same scripts directory (works inside Blender).` connect `Load ``common.py`` from the same scripts directory (works inside Blender).` to `create_animation.py`, `import_base_glb`, `modify_materials.py`, `scaffold_presenter_blend.py`, `add_stub_shape_keys.py`, `export_mesh_for_mixamo.py`, `export_glb.py`, `validate_rig.py`?**
  _High betweenness centrality (0.063) - this node is a cross-community bridge._
- **Why does `three` connect `AvatarRuntime.ts` to `AvatarScene.tsx`, `package.json`?**
  _High betweenness centrality (0.043) - this node is a cross-community bridge._
- **Why does `AvatarRuntime` connect `AvatarRuntime` to `AvatarScene.tsx`, `AvatarRuntime.ts`, `AudioController`?**
  _High betweenness centrality (0.030) - this node is a cross-community bridge._
- **What connects `StatusPanelProps`, `SemanticExpression`, `SemanticGesture` to the rest of the system?**
  _97 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `AvatarScene.tsx` be split into smaller, more focused modules?**
  _Cohesion score 0.058653846153846154 - nodes in this community are weakly interconnected._
- **Should `AvatarRuntime.ts` be split into smaller, more focused modules?**
  _Cohesion score 0.06944444444444445 - nodes in this community are weakly interconnected._
- **Should `AvatarRuntime` be split into smaller, more focused modules?**
  _Cohesion score 0.05584415584415584 - nodes in this community are weakly interconnected._