"""Async SQLAlchemy engine + session factory for PostgreSQL."""

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.core.config import settings
from app.models.base import Base

_engine = None
_sessionmaker = None


def get_engine():
    global _engine
    if _engine is None and settings.database_url:
        _engine = create_async_engine(
            settings.database_url,
            echo=settings.debug,
            pool_size=5,
            max_overflow=10,
        )
    return _engine


def get_sessionmaker():
    global _sessionmaker
    if _sessionmaker is None:
        engine = get_engine()
        if engine is not None:
            _sessionmaker = async_sessionmaker(engine, expire_on_commit=False)
    return _sessionmaker


async def create_tables():
    """Create all tables if they don't exist (idempotent)."""
    engine = get_engine()
    if engine is None:
        return
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def dispose_engine():
    """Clean up the engine on app shutdown."""
    global _engine, _sessionmaker
    if _engine is not None:
        await _engine.dispose()
        _engine = None
        _sessionmaker = None
