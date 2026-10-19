"""FastAPI application entrypoint."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import health, plans
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
    app.include_router(health.router)
    app.include_router(plans.router, prefix="/api/v1")
    return app


app = create_app()
