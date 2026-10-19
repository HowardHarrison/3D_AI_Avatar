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
| `npm run avatar:inspect` | Inventory the open `presenter.blend` (needs Blender on PATH) |
| `npm run avatar:validate-rig` | Validate bones / shape keys / clips on the `.blend` |
| `npm run avatar:export` | Export to `blender/exports/tmp/presenter.glb` |
| `npm run avatar:validate-export` | Validate the temp GLB (Python only) |
| `npm run avatar:promote` | Copy validated temp GLB → exports + `frontend/public` |
| `npm run avatar:release` | export → validate-export → promote |
| `npm run avatar:scaffold` | Regenerate learning `presenter.blend` (not production) |

Typical Blender release (from `frontend/`, after `presenter.blend` exists):

```bash
npm run avatar:release
npm run dev
```

End-to-end example (change suit color): [docs/blender-pipeline.md](docs/blender-pipeline.md#example-change-suit-color).

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

## Backend (FastAPI)

Scaffold under `backend/` (clean architecture; sample plan only — no LLM yet):

```bash
cd backend
copy .env.example .env
uv sync
uv run uvicorn app.main:app --reload --port 8000
```

See [backend/README.md](backend/README.md).

## Architecture in one line

Blender authors assets → GLB is the boundary → React Three Fiber renders → Avatar runtime plays semantic clips → backend/LLM will send timed semantic instruction plans (and later face/outfit presets).

Overall architecture (faces, clothes, backend plans, diagrams): [MVP_Phase_1.md](MVP_Phase_1.md).

Layer summary: [docs/architecture.md](docs/architecture.md).
