# Backend — Avatar News Presenter API

TapTube-style **clean architecture** FastAPI app. Produces semantic `AnimationPlan` JSON for the web (and later mobile) clients. No LLM / TTS / LangChain in this scaffold yet.

## Layout

```
app/
├── api/             # FastAPI routes + request/response schemas
├── core/            # settings, logging, exceptions
├── domain/          # models + provider interfaces (no SDKs)
├── infrastructure/  # external adapters (LangChain later)
├── prompts/         # prompt templates (empty until LLM step)
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

- Health: http://localhost:8000/health
- Sample plan: http://localhost:8000/api/v1/plans/sample
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

- Wire `LlmProvider` / `TtsProvider` implementations
- Optional LangChain adapter under `infrastructure/langchain/`
- Auth and mobile-oriented session endpoints
