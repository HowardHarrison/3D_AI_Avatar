# `frontend/src` layout

This is a conventional React frontend tree for the stylized chatbot avatar.

| Folder | Role | Allowed | Must not contain |
| --- | --- | --- | --- |
| `App.tsx` | Application shell | `App` component | Scene, runtime, debug buttons |
| `pages/` | Screens | Compose layout + features | Mixer, morphs, `useFrame` |
| `routes/` | Routing | Which page to render | Runtime classes |
| `layouts/` | Page chrome | `main.page` wrapping children | AvatarRuntime |
| `components/` | Shared presentational DOM | Props-only UI (`StatusPanel`) | Avatar imports beyond props |
| `features/avatar/` | Avatar feature | R3F, debug UI, avatar hooks/types | HTTP secrets |
| `features/chat/` | Chat UI + talk reaction + mic STT | Panel, hooks, Web Speech, semantic avatar calls | Mixer / morph math |
| `api/` | HTTP clients | `postChatTurn` etc. | Secrets, React |
| `services/avatar/` | Imperative runtime | Classes: mixer, facial, idle, audio | JSX |
| `constants/` | Config | avatar, studio, Vite env | Secrets |
| `utils/` | Shared helpers | `logger` | React components |
| `types/` | Semantic contracts | Gesture names, `AvatarController`, plans | Mixer implementation |
| `styles/` | Global CSS | `App.css` | — |
| `tests/` | Vitest | Mirrors `api/` / `services/` paths | — |

**Rule:** UI talks to `AvatarController` only. Only `features/avatar/components/Avatar.tsx` constructs `AvatarRuntime`.

Vite entry is `src/main.tsx`; shell is `src/App.tsx`. Dev proxy: `/api` → backend `:8000`.
