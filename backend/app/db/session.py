"""Async database engine and session management."""

from __future__ import annotations

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.config import get_settings
from app.core.logging import get_logger

logger = get_logger(__name__)

# Module-level engine and session factory (initialized in lifespan)
_engine: AsyncEngine | None = None
_session_factory: async_sessionmaker[AsyncSession] | None = None


def get_engine() -> AsyncEngine:
    """Return the global async engine.

    Raises:
        RuntimeError: If the engine has not been initialized.
    """
    if _engine is None:
        raise RuntimeError("Database engine is not initialized. Call init_db() first.")
    return _engine


def get_session_factory() -> async_sessionmaker[AsyncSession]:
    """Return the global session factory.

    Raises:
        RuntimeError: If the session factory has not been initialized.
    """
    if _session_factory is None:
        raise RuntimeError("Session factory is not initialized. Call init_db() first.")
    return _session_factory


async def init_db() -> None:
    """Create the async engine and session factory.

    Called once during application startup.
    """
    global _engine, _session_factory

    settings = get_settings()
    database_url = settings.get_database_url()

    logger.info("initializing_database_engine", url=database_url.split("@")[-1])

    _engine = create_async_engine(
        database_url,
        echo=settings.app_debug,
        pool_pre_ping=True,
        pool_size=5,
        max_overflow=10,
    )

    _session_factory = async_sessionmaker(
        bind=_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False,
        autocommit=False,
    )

    logger.info("database_engine_ready")


async def close_db() -> None:
    """Dispose of the engine and clear module state.

    Called during application shutdown.
    """
    global _engine, _session_factory

    if _engine is not None:
        logger.info("closing_database_engine")
        await _engine.dispose()
        _engine = None
        _session_factory = None
        logger.info("database_engine_closed")


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency that yields an async database session.

    Usage:
        @router.get("/items")
        async def list_items(db: AsyncSession = Depends(get_db)):
            ...
    """
    session_factory = get_session_factory()
    async with session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


async def check_database() -> str:
    """Simple connectivity check used by the readiness probe.

    Returns:
        "ok" if the database responds, otherwise an error message.
    """
    try:
        engine = get_engine()
        async with engine.connect() as conn:
            await conn.execute(__import__("sqlalchemy").text("SELECT 1"))
        return "ok"
    except Exception as exc:  # noqa: BLE001
        logger.warning("database_health_check_failed", error=str(exc))
        return f"error: {exc.__class__.__name__}"
