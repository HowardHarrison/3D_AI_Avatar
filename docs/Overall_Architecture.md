# Stylized Chatbot Avatar — Overall Architecture

This document is the **project architecture** for an interactive **stylized** 3D chatbot avatar (Snapchat / Bitmoji-like look). It describes system boundaries, data flows, and how the existing semantic runtime extends to chat (text/voice), customized looks, and optional timed instruction plans.

**Product pivot (Phase 0):** primary UX is **conversation** (text first, then voice). The earlier “news presenter + AnimationPlan” path remains a valid **optional scripted mode**, not the main product story.

Implementation is incremental (learn-by-building). Not every capability below is fully coded yet; items marked **Planned** are approved architecture, not unfinished guesses.

Related docs:

- [docs/architecture.md](docs/architecture.md) — layer summary
- [docs/avatar-art-contract.md](docs/avatar-art-contract.md) — stylized look + bone/clip/morph contract
- [docs/blender-pipeline.md](docs/blender-pipeline.md) — Blender → GLB automation
- [docs/avatar-spec.md](docs/avatar-spec.md) — asset and semantic API notes
- [AGENTS.md](AGENTS.md) — one-step implementation rule for coding agents

---

## 1. Product Goal

Build a browser-based **interactive chatbot avatar** that:

1. Loads a **stylized** humanoid from a validated **GLB** (skeleton + motion; looks swapable in Three.js)
2. Plays **semantic** behaviors (idle, talk reaction, gestures, expressions, head, gaze, audio)
3. Converses with the user via **text** first, then **voice in/out** (STT / TTS) without exposing bones/clips to the UI
4. Optionally accepts a timed **AnimationPlan** for scripted performances (legacy presenter path)
5. Supports **visual customization** (materials / accessories) through clear asset + runtime boundaries
6. Stays maintainable for a developer + AI coding agent (Blender Python for structure, TypeScript/JSON for behavior)

---

## 2. Core Principles

1. **Edit sources, not compiled GLBs** — JSON, TypeScript, and Blender Python are primary; `presenter.glb` is an export.
2. **Blender authors assets; the browser runs them** — no Blender in the request path.
3. **Semantic commands only** — `playGesture("emphasize")`, `setExpression("serious")`, never bone indexes or clip array positions.
4. **Separate look from behavior** — mesh/materials/morphs vs gestures/idle/plans.
5. **Inspect → backup → modify → validate → export temp → promote** for asset changes.
6. **Backend sends plans, not renderer details** — emotion/gesture/head/gaze (+ later outfit/face presets), never Mixamo bone paths or Three.js objects.
7. **Grow in phases** — local runtime first; chat → TTS → STT → skins (see roadmap below).
8. **Stylized over photoreal** — cartoon proportions and soft/flat materials; see [avatar-art-contract.md](avatar-art-contract.md).

---

## 3. System Context

```mermaid
flowchart LR
  subgraph Authors["Authoring"]
    DEV[Developer / AI Agent]
    BL[Blender + Python scripts]
    DEF[JSON / TypeScript definitions]
  end

  subgraph Assets["Asset boundary"]
    GLB["presenter.glb stand-in → stylized GLB"]
  end

  subgraph Runtime["Browser"]
    UI[Chat UI + debug panel]
    RT[AvatarRuntime]
    R3F[React Three Fiber / Three.js]
  end

  subgraph Backend["Backend"]
    API[API / Orchestrator]
    LLM[LLM chat turns]
    TTS[TTS / media]
    STT[STT - Planned]
  end

  DEV --> BL
  DEV --> DEF
  BL --> GLB
  DEF --> RT
  GLB --> RT
  UI --> RT
  RT --> R3F
  UI <-->|chat turns| API
  LLM --> API
  TTS --> API
  STT -.-> API
  API -.->|optional AnimationPlan| UI
```

### Roadmap (learning-sized phases)

| Phase | Focus | Status |
| --- | --- | --- |
| 0 | Product goal + art/naming contract; keep stand-in GLB | Done |
| 1 | Stylized avatar art + bust framing | Done |
| 2 | Text chat loop → avatar talk/idle | Done |
| 3 | TTS → `AudioController` + mouth morphs | Done |
| 4 | Voice in (STT) | **In progress** (4.1 browser mic) |
| 5 | Three.js skins / material presets | Planned |
| 6 | Polish (streaming, barge-in, richer gestures) | Planned |

---

## 4. Logical Architecture

```mermaid
flowchart TB
  subgraph Web["Web application layer"]
    REACT[React + Vite]
    DEBUG[Debug panel]
    PLAN_UI[Plan consumer - Planned]
  end

  subgraph RuntimeLayer["Avatar runtime layer"]
    CTRL[AvatarController API]
    ANIM[AnimationController]
    FACE[FacialController]
    IDLE[IdleController]
    AUD[AudioController]
    PLAYER[AnimationPlanPlayer - Planned]
    OUTFIT[AppearanceController - Planned]
  end

  subgraph AssetLayer["Asset authoring layer"]
    BPY[Blender automation]
    SRC["presenter.blend"]
    EXP["exports/tmp → validate → promote"]
  end

  REACT --> CTRL
  DEBUG --> CTRL
  PLAN_UI --> PLAYER
  PLAYER --> CTRL
  CTRL --> ANIM
  CTRL --> FACE
  CTRL --> IDLE
  CTRL --> AUD
  CTRL --> OUTFIT
  BPY --> SRC
  SRC --> EXP
  EXP -->|GLB| RuntimeLayer
```

| Layer | Responsibility |
| --- | --- |
| Web | Pages, debug UI, config, later fetch/WebSocket for plans |
| Avatar runtime | Semantic API → mixers, morphs, bones, audio, appearance |
| Definitions | Gesture/expression names, materials/outfit presets, schemas |
| Blender authoring | Rig, mesh, real facial morphs, clothing meshes/textures, export |
| Backend (planned) | Produce `AnimationPlan` (+ optional appearance intents) |

---

## 5. Repository Layout (actual)

The npm app lives in **`frontend/`** (not an `apps/` monorepo).

```text
AI_3D_Avatar/
├── frontend/                          # Vite + React + R3F
│   ├── public/avatars/presenter.glb   # Runtime GLB (promoted)
│   ├── public/audio/
│   └── src/
│       ├── features/avatar/           # R3F scene + debug UI
│       ├── services/avatar/           # AvatarRuntime, controllers
│       ├── types/                     # AvatarController, AnimationPlan
│       └── constants/
├── blender/
│   ├── source/presenter.blend         # Authoring source
│   ├── scripts/                       # inspect, validate, export, modify, …
│   ├── definitions/                   # bone rename maps, etc.
│   └── exports/                       # tmp + candidate GLB, Mixamo uploads
├── docs/
├── MVP_Phase_1.md                     # This architecture document
├── AGENTS.md
└── README.md
```

---

## 6. End-to-End Data Flows

### 6.1 Asset pipeline (Blender → browser)

```mermaid
sequenceDiagram
  participant Agent as AI Agent / Developer
  participant Blender as Blender scripts
  participant Tmp as exports/tmp
  participant Val as validate_export
  participant Pub as frontend/public/avatars

  Agent->>Blender: inspect / modify / create clips
  Blender->>Blender: save_versioned_blend + validate_rig
  Blender->>Tmp: export_glb.py
  Agent->>Val: validate_export.py
  Val-->>Agent: PASS / ERROR
  Agent->>Pub: promote_export.py
  Note over Pub: Browser loads presenter.glb
```

### 6.2 Backend instruction array → avatar performance (target)

```mermaid
sequenceDiagram
  participant BE as Backend / LLM
  participant Web as React app
  participant Parse as parseAnimationPlan
  participant Player as AnimationPlanPlayer
  participant RT as AvatarController

  BE->>Web: POST/WS AnimationPlan JSON
  Web->>Parse: parseAnimationPlan(raw)
  Parse-->>Web: typed plan or error
  Web->>Player: playPlan(plan)
  loop each segment at start time
    Player->>RT: setExpression / playGesture / setHeadMotion / setGaze
  end
  RT-->>Web: getStatus() for debug
```

**Status today:** `AnimationPlan` types and `parseAnimationPlan` exist. **AnimationPlanPlayer** and backend transport are **Planned**.

### 6.3 Appearance change (face / clothes)

```mermaid
flowchart TD
  REQ[Change face or clothes]
  REQ --> DEC{Where is the change?}
  DEC -->|Color / preset already in GLB| RT[Runtime AppearanceController]
  DEC -->|New morphs, textures, meshes| BL[Blender Python pipeline]
  RT --> UI[Immediate UI update]
  BL --> VAL[Validate + export + promote]
  VAL --> GLB[New presenter.glb]
  GLB --> UI
```

---

## 7. Semantic Runtime API

UI, debug panel, plan player, and future backend adapters must use only this surface (names may grow; indexes never appear):

| Command | Purpose |
| --- | --- |
| `playGesture(name)` | One-shot body gesture |
| `setExpression(name)` | Facial morph preset |
| `setHeadMotion(name)` | Nod / turn / tilt |
| `setGaze(target)` | Look target |
| `startSpeaking()` / `stopSpeaking()` | Speech state hooks |
| `loadAudio` / `playAudio` / `pauseAudio` / `stopAudio` | Local audio (Phase 1) |
| `reset()` | Return to idle baseline |
| `playPlan(plan)` | **Planned** — run timed segment array |
| `setOutfit(id)` / `setFacePreset(id)` | **Planned** — appearance presets |

Current gesture / expression / head / gaze name sets live in `frontend/src/types/animation.ts` and `AnimationRegistry.ts`.

---

## 8. Backend Instruction Plans

### 8.1 Contract

Backend (or a mock file) sends an **array of timed segments**, not a list of bone keyframes.

```json
{
  "segments": [
    {
      "start": 0,
      "end": 2.0,
      "emotion": "serious",
      "gaze": "camera"
    },
    {
      "start": 2.0,
      "end": 4.5,
      "gesture": "emphasize",
      "headMotion": "nod",
      "emotion": "serious"
    },
    {
      "start": 4.5,
      "end": 7.0,
      "emotion": "positive",
      "gesture": "openHand",
      "headMotion": "tiltLeft"
    }
  ]
}
```

Optional later fields (same semantic style):

```json
{
  "start": 0,
  "end": 10,
  "emotion": "neutral",
  "outfit": "suit_navy",
  "facePreset": "presenter_a"
}
```

### 8.2 Rules

- Times are seconds from plan start (`start` ≤ `end`).
- Unknown semantic names are rejected by `parseAnimationPlan`.
- Player maps each segment onto `AvatarController` at `start` (and may clear/replace at `end` as designed).
- Backend must not send morph indexes, clip indexes, or Three.js node names.

### 8.3 Implementation stages

| Stage | Deliverable |
| --- | --- |
| Done | `AnimationPlan` / `AnimationSegment` types |
| Done | `parseAnimationPlan` + unit tests |
| Planned | `AnimationPlanPlayer` + `playPlan` on controller |
| Planned | Debug “load sample plan” button |
| Planned | HTTP or WebSocket client to a backend |
| Later | LLM generates plans; TTS clock aligns segments |

---

## 9. Customized Face

### 9.1 Goals

- Swap or refine the presenter’s face without rewriting the runtime
- Drive expressions through stable morph target names (`mouth_smile`, `brow_up`, …)
- Optionally select a **face preset** from UI/backend when multiple faces exist

### 9.2 Architecture split

| Concern | Owner |
| --- | --- |
| Face mesh, textures, real blendshapes | Blender (authoring) |
| Morph name contract | `blender/scripts/contracts.py` + docs |
| Applying expression weights | `FacialController` |
| Choosing preset “Presenter A/B” | **Planned** `AppearanceController` / definitions JSON |

### 9.3 Paths to a custom face

1. **Author morphs on current character** — sculpt real shape keys in Blender; keep contract names; export → promote.
2. **Replace character** — import rigged GLB/FBX (e.g. Mixamo / Ready Player Me), rename bones, add morphs, release.
3. **Runtime face preset (Planned)** — multiple head meshes or morph/texture sets in one GLB (or swapped GLB URL), selected by `setFacePreset("id")`.

### 9.4 Constraints

- Mixamo bodies often lack production facial morphs; stubs exist only for contract/testing.
- Photo-to-face pipelines stay **outside** the runtime (external tool → import pipeline).
- Do not scatter morph target indexes in React components.

---

## 10. Avatar Clothing

### 10.1 Goals

- Change suit/outfit appearance without breaking the rig or semantic API
- Prefer **runtime overrides** for color/presets when the GLB already exposes materials
- Use Blender when clothes need new meshes, UVs, or texture sets

### 10.2 Architecture split

| Concern | Owner |
| --- | --- |
| Clothing meshes, UVs, textures, material slots | Blender |
| Material naming (`Suit`, `Shirt`, …) | Asset contract / definitions |
| Recolor / switch preset at runtime | **Planned** `AppearanceController` |
| Bake new materials into GLB | `modify_materials.py` + export pipeline |

### 10.3 Paths to change clothes

1. **Color change (simple)** — Blender `modify_materials.py` or runtime material color override (**Planned** in UI).
2. **Outfit preset** — named material/texture sets or hidden mesh groups; `setOutfit("suit_navy")`.
3. **Full wardrobe swap** — separate clothing meshes skinned to the same armature; show/hide or swap in runtime.

### 10.4 Constraints

- A single atlas texture that mixes skin + cloth limits recoloring; split materials in Blender when wardrobe matters.
- Backend may request `outfit` in a plan segment; it must not send shader graphs or texture URLs into the mixer blindly (validate against an allow-list).

---

## 11. Blender Automation Strategy

Authoring stays programmable:

```text
inspect_scene → modify_* / create_animation / apply_rename_map
  → save_versioned_blend → validate_rig
  → export_glb (tmp) → validate_export → promote_export
```

Key scripts live under `blender/scripts/` (MVP docs that say `automation/` mean this folder). See [docs/blender-pipeline.md](docs/blender-pipeline.md).

npm helpers from `frontend/`: `avatar:inspect`, `avatar:validate-rig`, `avatar:export`, `avatar:validate-export`, `avatar:promote`, `avatar:release`, `avatar:scaffold`, `avatar:export-mixamo`, `avatar:import-rigged`.

---

## 12. Animation and Appearance Strategy

```mermaid
flowchart LR
  subgraph Semantic["Semantic layer"]
    G[Gestures]
    E[Expressions]
    H[Head / Gaze]
    O[Outfit / Face preset]
    P[AnimationPlan]
  end

  subgraph Execution["Runtime execution"]
    CLIPS[GLB animation clips]
    MORPHS[Morph targets]
    MATS[Materials / meshes]
  end

  G --> CLIPS
  H --> CLIPS
  E --> MORPHS
  O --> MATS
  P --> G
  P --> E
  P --> H
  P --> O
```

- **Clips** — idle, gestures, head motions (Blender or stub generators).
- **Morphs** — facial expressions (and later visemes).
- **Materials/meshes** — clothes and face look.
- **Plans** — timed orchestration from backend/LLM.

---

## 13. Phase Map

| Phase | Focus | Backend? |
| --- | --- | --- |
| **Phase 1 (current foundation)** | GLB load, semantic API, idle, gestures, expressions, head, local audio, debug panel, Blender pipeline | No |
| **Phase 1b (next architecture slices)** | `AnimationPlanPlayer`, sample plans, appearance presets (outfit/face) | Mock or local JSON |
| **Phase 2** | FastAPI (or similar), plan transport, TTS clock | Yes |
| **Phase 3+** | LLM planning, lip-sync, subtitles, multilingual, embedding | Yes |

Phase 1 must not implement full LLM/TTS/video stacks, but **must keep APIs ready** for plans and appearance.

---

## 14. Web and Runtime Notes

- Per-frame work stays in `AvatarRuntime.update` / `useFrame` — not React `setState` every frame.
- Debug panel samples status a few times per second and only calls `AvatarController`.
- Only the avatar feature constructs `AvatarRuntime` (see `features/avatar`).
- Missing clips/morphs/materials produce warnings and safe no-ops where possible.

---

## 15. Testing and Validation

- **Unit:** definition validation, `parseAnimationPlan`, registries, state machine.
- **Blender:** `inspect_scene`, `validate_rig`, `validate_export` (PASS/WARNING/ERROR lines).
- **Manual:** presenter loads, gestures, expressions, head, audio, plan playback (when built), outfit/face presets (when built).
- **Rule:** failed export validation must not promote over a working runtime GLB.

---

## 16. Engineering Rules

- Do not put all avatar logic in one React component.
- Do not use clip indexes or raw morph indexes in UI/backend payloads.
- Do not overwrite `presenter.blend` or runtime GLB without backup/validation.
- Do not launch Blender for ordinary browser interactions.
- Prefer runtime material/outfit presets for clothes color; use Blender for structural clothing/face work.
- Backend plans are semantic only.

---

## 17. Definition of Done (architecture milestones)

### Foundation (Phase 1)

- [x] Local Vite app loads `presenter.glb`
- [x] Semantic runtime API + debug panel
- [x] Blender inspect → validate → export → promote pipeline
- [x] `AnimationPlan` types + `parseAnimationPlan`
- [ ] Documented overall architecture (this file)

### Planned next

- [ ] `AnimationPlanPlayer` + `playPlan`
- [ ] Debug/mock plan from JSON file or paste
- [ ] Appearance API: outfit and/or face preset
- [ ] Asset guidance: split materials for clothes; real facial morphs or multi-face presets
- [ ] Backend endpoint or WebSocket delivering `AnimationPlan`

---

## 18. Final Division of Responsibilities

| System | Owns |
| --- | --- |
| **Blender** | Geometry, rig, facial morph authorship, clothing meshes/textures |
| **Blender Python** | Inspect, safe modify, validate, export |
| **GLB** | Runtime distribution format |
| **JSON / TS definitions** | Names, presets, schemas |
| **AvatarRuntime** | Semantic → clips/morphs/materials |
| **React** | UI, lifecycle, plan fetch UI |
| **Backend (future)** | Orchestration, LLM plans, TTS timing |
| **LLM (future)** | High-level presenter plans in semantic JSON |

The objective is not to rebuild DCC tools in the browser. The objective is a **clear boundary**: author looks in Blender, drive behavior with semantic plans, and keep the backend ignorant of bones and shaders.
