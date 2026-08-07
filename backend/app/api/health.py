"""Health check endpoints."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, status
from pydantic import BaseModel, Field

from app.config import get_settings
from app.core.logging import get_logger
from app.db import check_database

router = APIRouter(tags=["Health"])
logger = get_logger(__name__)


class HealthResponse(BaseModel):
    """Standard health check response."""

    status: str = Field(..., description="Overall service status")
    version: str = Field(..., description="Application version")
    environment: str = Field(..., description="Runtime environment")
    checks: dict[str, Any] = Field(default_factory=dict, description="Individual dependency checks")


@router.get(
    "/health",
    response_model=HealthResponse,
    status_code=status.HTTP_200_OK,
    summary="Liveness probe",
    description="Returns 200 if the application process is alive.",
)
async def health() -> HealthResponse:
    """Basic liveness check.

    Used by container orchestrators to know the process is running.
    """
    settings = get_settings()
    return HealthResponse(
        status="ok",
        version=settings.app_version,
        environment=settings.app_env,
        checks={},
    )


@router.get(
    "/ready",
    response_model=HealthResponse,
    status_code=status.HTTP_200_OK,
    summary="Readiness probe",
    description="Returns 200 when the application is ready to accept traffic (DB reachable).",
)
async def ready() -> HealthResponse:
    """Readiness check.

    Verifies database connectivity. Redis check will be added in a later batch.
    """
    settings = get_settings()
    checks: dict[str, Any] = {
        "application": "ok",
        "database": await check_database(),
    }

    overall = "ok" if all(v == "ok" for v in checks.values()) else "degraded"

    logger.debug("readiness_check", status=overall, checks=checks)

    return HealthResponse(
        status=overall,
        version=settings.app_version,
        environment=settings.app_env,
        checks=checks,
    )
