# Backend — Chatbot Avatar API

TapTube-style **clean architecture** FastAPI app for the stylized chatbot avatar. Today: OpenAI-compatible `LLMProvider`, TTS ports, and semantic `AnimationPlan` helpers (optional scripted mode). Next product path: **chat turns** (text → reply; later STT/TTS). `GET /plans/sample` remains a hardcoded integration fixture.

## Layout

```
app/
├── api/             # FastAPI routes + request/response schemas
├── core/            # settings, logging, exceptions
├── domain/          # models + provider interfaces (no SDKs)
├── infrastructure/  # external adapters (openai_compatible; LangChain later)
├── prompts/         # prompt templates for LLM-backed use cases
├── services/        # use cases / orchestration
├── utils/
└── main.py
```

Dependency direction: `api` → `services` → `domain` ← `infrastructure`.

## Setup

Requires Python 3.12+ and [uv](https://github.com/astral-sh/uv) (or pip).

```bash
cd backend
copy .env.example .env
uv sync
uv run uvicorn app.main:app --reload --port 8000
```

Or from the repo root with Docker (see root `docker-compose.yml`):

```bash
docker compose up backend-dev
# or: docker compose up --build backend
```

Set `LLM_API_KEY` in `.env` when you are ready to call a model (OpenAI by default).
Do not put LLM keys in the frontend or any `VITE_*` variable. Config is loaded via
`app.core.settings.Settings` (`LLM_PROVIDER`, `LLM_API_KEY`, `LLM_MODEL`, optional `LLM_BASE_URL`).

Adapters: `OpenAICompatibleLLMProvider`, `OpenAICompatibleTtsProvider`
(`app.infrastructure.openai_compatible`).

- Chat turn: `POST /api/v1/chat/turns` —
  `{ "message": "...", "history": [{ "role": "user"|"assistant", "content": "..." }] }`
  → `{ "reply": "..." }` (`history` optional; prior turns only)
- TTS: `POST /api/v1/tts/synthesize` — `{ "text": "..." }` →
  `{ "audioUrl": "/api/v1/tts/audio/<id>.mp3", "durationSeconds": ... }`
  then `GET` the `audioUrl`. Uses `TTS_API_KEY` or falls back to `LLM_API_KEY`.
  Cache dir: `backend/.tts_cache/` (gitignored).
- Plan script: `POST /api/v1/plans/generate-text`
- Plan JSON: `POST /api/v1/plans/generate`
- Optional `LLM_BASE_URL` / `TTS_BASE_URL` for OpenAI-compatible gateways

- Health: http://localhost:8000/health
- OpenAPI: http://localhost:8000/docs

Without uv:

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -e ".[dev]"
uvicorn app.main:app --reload --port 8000
```

## Next (not in this step)

- STT (voice in)
- Optional LangChain adapter under `infrastructure/langchain/`
