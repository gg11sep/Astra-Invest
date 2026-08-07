"""Structured logging configuration using structlog."""

from __future__ import annotations

import logging
import sys
from typing import Any

import structlog
from structlog.types import Processor

from app.config import get_settings


def setup_logging() -> None:
    """Configure structured logging for the application.

    In development we use a human-friendly console renderer.
    In other environments we emit JSON for log aggregation systems.
    """
    settings = get_settings()

    shared_processors: list[Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.UnicodeDecoder(),
    ]

    if settings.log_format == "console" or settings.is_development:
        # Human-readable output for local development
        processors: list[Processor] = [
            *shared_processors,
            structlog.dev.ConsoleRenderer(colors=True),
        ]
    else:
        # Machine-readable JSON for production
        processors = [
            *shared_processors,
            structlog.processors.format_exc_info,
            structlog.processors.JSONRenderer(),
        ]

    structlog.configure(
        processors=processors,
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    # Configure standard library logging to go through structlog
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, settings.log_level.upper()),
    )

    # Quiet noisy third-party loggers
    for noisy_logger in ("uvicorn.access", "httpx", "httpcore", "asyncio"):
        logging.getLogger(noisy_logger).setLevel(logging.WARNING)


def get_logger(name: str | None = None) -> Any:
    """Return a structured logger.

    Args:
        name: Optional logger name (usually __name__).

    Returns:
        A bound structlog logger.
    """
    return structlog.get_logger(name)
