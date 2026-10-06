# Architecture

Phase 1 establishes layer boundaries so later AI features do not rewrite the avatar runtime.

```text
Blender (authoring)
    → presenter.glb (asset boundary)
    → React / Vite (UI, lifecycle)
    → React Three Fiber (scene, camera, lights)
    → AvatarRuntime (semantic API)
        → AnimationController
        → FacialController
        → IdleController
        → AudioController
    → Three.js / GPU
```

## Responsibilities

| Layer | Owns |
| --- | --- |
| React | Pages, debug panel, configuration, load errors |
| R3F Canvas | Camera, lights, studio meshes, `useFrame` |
| AvatarRuntime | Mixers, morphs, bones, idle timers, audio element |
| `frontend/src/types` | Gesture/expression names, animation plans, viseme types |

Per-frame updates stay in `AvatarRuntime.update`. The debug panel samples status about four times per second and must not `setState` on every animation frame.

Frontend folders in `frontend/src` (conventional React tree; one feature: the 3D presenter):

| Folder | Layer |
| --- | --- |
| `App.tsx` / `pages/` | Shell and screens |
| `routes/` | Which page to render |
| `layouts/` | Page chrome (`PresenterLayout`) |
| `components/` | Shared presentational DOM |
| `features/avatar/` | R3F + debug UI; talks to `AvatarController` |
| `services/avatar/` | Runtime classes; no JSX |
| `constants/` | Avatar, studio, Vite env |
| `utils/` | Logger |
| `types/` | Semantic contracts (`AvatarController`, gesture names) |
| `styles/` | Global CSS |
| `tests/` | Vitest, mirroring `services/` |

`store/`, `api/`, and unused feature domains (`auth`, `users`, `dashboard`) are omitted: Phase 1 has no Redux, HTTP API, or auth. Only `Avatar.tsx` constructs `AvatarRuntime`.

See [frontend/src/README.md](../frontend/src/README.md).

## Future attachment points

- `startSpeaking` / `stopSpeaking` on `AvatarController`
- `VisemeEvent` in `frontend/src/types`
- `parseAnimationPlan` for LLM or FastAPI payloads

Those systems must emit `{ "emotion", "gesture", "headMotion", "gaze" }`, never bone rotations.
