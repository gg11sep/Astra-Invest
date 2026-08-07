"""Astra-Invest FastAPI application entrypoint."""

from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import __version__
from app.api.health import router as health_router
from app.api.companies import router as companies_router
from app.api.auth import router as auth_router
from app.api.portfolios import router as portfolios_router
from app.api.transactions import router as transactions_router
from app.api.watchlists import router as watchlists_router
from app.api.screening import router as screening_router
from app.api.prices import router as prices_router
from app.api.valuation import router as valuation_router
from app.api.market_data import router as market_data_router
from app.api.agents import router as agents_router
from app.config import get_settings
from app.core.logging import get_logger, setup_logging
from app.db import close_db, init_db

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Application lifespan handler.

    Runs startup and shutdown logic.
    """
    settings = get_settings()
    logger.info(
        "application_starting",
        app_name=settings.app_name,
        version=settings.app_version,
        environment=settings.app_env,
    )

    await init_db()

    yield

    await close_db()
    logger.info("application_shutting_down")


def create_application() -> FastAPI:
    """Application factory.

    Creates and configures the FastAPI instance.
    This pattern makes testing and different deployment modes easier.
    """
    settings = get_settings()

    # Configure logging as early as possible
    setup_logging()

    app = FastAPI(
        title=settings.app_name,
        version=__version__,
        description=(
            "AI-native investment research platform. "
            "Configurable strategies, multi-agent research, and explainable recommendations."
        ),
        docs_url="/docs" if not settings.is_production else None,
        redoc_url="/redoc" if not settings.is_production else None,
        openapi_url="/openapi.json" if not settings.is_production else None,
        lifespan=lifespan,
    )

    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Routers
    app.include_router(health_router, prefix="/api/v1")
    app.include_router(companies_router, prefix="/api/v1")
    app.include_router(auth_router, prefix="/api/v1")
    app.include_router(portfolios_router, prefix="/api/v1")
    app.include_router(transactions_router, prefix="/api/v1")
    app.include_router(watchlists_router, prefix="/api/v1")
    app.include_router(screening_router, prefix="/api/v1")
    app.include_router(prices_router, prefix="/api/v1")
    app.include_router(valuation_router, prefix="/api/v1")
    app.include_router(market_data_router, prefix="/api/v1")
    app.include_router(agents_router, prefix="/api/v1")

    @app.get("/", include_in_schema=False)
    async def root() -> dict[str, str]:
        """Root endpoint — simple service identification."""
        return {
            "service": settings.app_name,
            "version": settings.app_version,
            "status": "running",
            "docs": "/docs",
        }

    return app


# Module-level app instance used by uvicorn / gunicorn
app = create_application()
