"""FastAPI application entrypoint."""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.routes import chat, health, plans
from app.core.exceptions import (
    ChatValidationError,
    LlmConfigurationError,
    LlmProviderError,
    PlanValidationError,
)
from app.core.logging import setup_logging
from app.core.settings import get_settings


def create_app() -> FastAPI:
    """Build and configure the ASGI application."""
    settings = get_settings()
    setup_logging(level=settings.log_level)

    app = FastAPI(title=settings.app_name, debug=settings.debug)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.exception_handler(LlmConfigurationError)
    async def llm_config_handler(
        _request: Request,
        exc: LlmConfigurationError,
    ) -> JSONResponse:
        """Missing/invalid LLM settings → 503."""
        return JSONResponse(status_code=503, content={"detail": str(exc)})

    @app.exception_handler(LlmProviderError)
    async def llm_provider_handler(
        _request: Request,
        exc: LlmProviderError,
    ) -> JSONResponse:
        """Upstream LLM failure → 502."""
        return JSONResponse(status_code=502, content={"detail": str(exc)})

    @app.exception_handler(PlanValidationError)
    async def plan_validation_handler(
        _request: Request,
        exc: PlanValidationError,
    ) -> JSONResponse:
        """Invalid plan / topic → 400."""
        return JSONResponse(status_code=400, content={"detail": str(exc)})

    @app.exception_handler(ChatValidationError)
    async def chat_validation_handler(
        _request: Request,
        exc: ChatValidationError,
    ) -> JSONResponse:
        """Invalid chat message → 400."""
        return JSONResponse(status_code=400, content={"detail": str(exc)})

    app.include_router(health.router)
    app.include_router(plans.router, prefix="/api/v1")
    app.include_router(chat.router, prefix="/api/v1")
    return app


app = create_app()
