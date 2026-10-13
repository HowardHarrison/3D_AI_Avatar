# Avatar News Presenter

Phase 1 MVP: a browser 3D news presenter loaded from a GLB, driven by a semantic TypeScript runtime. There is no LLM, TTS, or backend in this phase.

The npm project is **`frontend/`** (one Vite app, one `node_modules`). There is no `apps/` workspace and no `packages/shared`.

## Prerequisites

- Node.js 20 or newer
- npm 10 or newer
- Optional: Blender 3.6 LTS, 4.x, or 5.x on PATH (author `presenter.blend`, headless inspect/validate/export)
- Optional: Docker Desktop (Vite dev container or nginx preview)
- Optional: Python 3 (placeholder GLB / test audio generators)

Blender automation layout and safe export rules:
[docs/blender-pipeline.md](docs/blender-pipeline.md).

## Setup

```bash
git clone <repository>
cd AI_3D_Avatar/frontend
copy .env.example .env
npm install
npm run dev
```

Open http://localhost:5173

You should see a waist-up presenter (placeholder humanoid until you export your Blender character), idle breathing, blinks, and a debug panel.

## Scripts

Run these from `frontend/`:

| Command | Purpose |
| --- | --- |
| `npm run dev` | Vite development server |
| `npm run build` | Production build |
| `npm test` | Vitest unit tests |
| `npm run lint` | ESLint |
| `npm run generate:avatar` | Write placeholder GLB (exports + frontend public) |
| `npm run generate:audio` | Write `frontend/public/audio/test-presenter.mp3` |

Blender export path (after you have `presenter.blend`): export → validate → promote.
See [docs/blender-pipeline.md](docs/blender-pipeline.md).

## Docker

From the repo root:

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
