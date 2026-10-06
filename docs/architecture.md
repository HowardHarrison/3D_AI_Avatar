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
| Shared package | Gesture/expression names, animation plans, viseme types |

Per-frame updates stay in `AvatarRuntime.update`. The debug panel samples status about four times per second and must not `setState` on every animation frame.

## Future attachment points

- `startSpeaking` / `stopSpeaking` on `AvatarController`
- `VisemeEvent` in `@avatar/shared`
- `parseAnimationPlan` for LLM or FastAPI payloads

Those systems must emit `{ "emotion", "gesture", "headMotion", "gaze" }`, never bone rotations.
