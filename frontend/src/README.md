# `frontend/src` layout

This is a conventional React frontend tree. Phase 1 has **one feature**: the 3D presenter.

| Folder | Role | Allowed | Must not contain |
| --- | --- | --- | --- |
| `App.tsx` | Application shell | `App` component | Scene, runtime, debug buttons |
| `pages/` | Screens | Compose layout + feature | Mixer, morphs, `useFrame` |
| `routes/` | Routing | Which page to render | Runtime classes |
| `layouts/` | Page chrome | `main.page` wrapping children | AvatarRuntime |
| `components/` | Shared presentational DOM | Props-only UI (`StatusPanel`) | Avatar imports beyond props |
| `features/avatar/` | Presenter feature | R3F, debug UI, avatar hooks/types | HTTP, Redux |
| `services/avatar/` | Imperative runtime | Classes: mixer, facial, idle, audio | JSX |
| `constants/` | Config | avatar, studio, Vite env | Secrets |
| `utils/` | Shared helpers | `logger` | React components |
| `types/` | Semantic contracts | Gesture names, `AvatarController`, plans | Mixer implementation |
| `styles/` | Global CSS | `App.css` | — |
| `tests/` | Vitest | Mirrors `services/` paths | — |

**Rule:** UI in `features/avatar/components` talks to `AvatarController`. Only `features/avatar/components/Avatar.tsx` constructs `AvatarRuntime`.

Vite entry is `src/main.tsx`; shell is `src/App.tsx`. Avatar-specific hooks live in `features/avatar/hooks`.

We omitted `store/`, `api/`, and `features/auth|users|dashboard` because Phase 1 has no Redux, no HTTP API, and no auth. Empty folders would be fake domains.
