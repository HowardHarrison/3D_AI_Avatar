# Backend — Avatar News Presenter API

TapTube-style **clean architecture** FastAPI app. Produces semantic `AnimationPlan` JSON for the web (and later mobile) clients. OpenAI-compatible `LLMProvider` adapter is available; sample plans are still hardcoded (no LLM route yet).

## Layout

```
app/
├── api/             # FastAPI routes + request/response schemas
├── core/            # settings, logging, exceptions
├── domain/          # models + provider interfaces (no SDKs)
├── infrastructure/  # external adapters (openai_compatible; LangChain later)
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

Set `LLM_API_KEY` in `.env` when you are ready to call a model (OpenAI by default).
Do not put LLM keys in the frontend or any `VITE_*` variable. Config is loaded via
`app.core.settings.Settings` (`LLM_PROVIDER`, `LLM_API_KEY`, `LLM_MODEL`, optional `LLM_BASE_URL`).

Adapter: `OpenAICompatibleLLMProvider` (`app.infrastructure.openai_compatible`).
DI factory: `get_llm_provider()` in `app.api.dependencies` (not attached to a route yet).
Optional `LLM_BASE_URL` works with OpenAI-compatible gateways (OpenRouter, Azure-style proxies, local).

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

- Call `get_llm_provider()` from a service / route (e.g. generate plan text)
- Wire `TtsProvider` implementation
- Optional LangChain adapter under `infrastructure/langchain/`
- Auth and mobile-oriented session endpoints
