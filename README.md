# Avatar News Presenter

Phase 1 MVP: a browser 3D news presenter loaded from a GLB, driven by a semantic TypeScript runtime. There is no LLM, TTS, or backend in this phase.

## Prerequisites

- Node.js 20 or newer
- npm 10 or newer
- Optional: Blender 4.x (to author `presenter.blend`)
- Optional: Docker Desktop (Vite dev container or nginx preview)
- Optional: Python 3 (placeholder GLB / test audio generators)

## Setup

```bash
git clone <repository>
cd AI_3D_Avatar
copy .env.example .env
npm install
npm run dev
```

Open http://localhost:5173

You should see a waist-up presenter (placeholder humanoid until you export your Blender character), idle breathing, blinks, and a debug panel.

## Scripts

| Command | Purpose |
| --- | --- |
| `npm run dev` | Vite development server |
| `npm run build` | Production build |
| `npm test` | Vitest unit tests |
| `npm run lint` | ESLint |
| `npm run generate:avatar` | Write `blender/exports/presenter.glb` placeholder |
| `npm run generate:audio` | Write `apps/web/public/audio/test-presenter.mp3` |

After generating a new GLB, copy it:

`blender/exports/presenter.glb` → `apps/web/public/avatars/presenter.glb`

## Docker

```bash
docker compose up web-dev
```

Production-style static preview:

```bash
docker compose up --build web
```

Then open http://localhost:8080

## Architecture in one line

Blender authors assets → GLB is the boundary → React Three Fiber renders → Avatar runtime plays semantic clips → future AI will only send those semantic commands.

See [docs/architecture.md](docs/architecture.md).
