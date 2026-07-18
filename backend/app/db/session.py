from collections.abc import AsyncGenerator

from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

from app.core.config import settings

# NullPool: don't reuse connections across requests. Async SQLAlchemy
# connections bind to the event loop they were first used on; with
# pooling enabled, pytest-asyncio's per-test-file event loops can end up
# reusing a connection from a now-closed loop ("attached to a different
# loop" errors). NullPool trades a little connection overhead for
# avoiding that whole class of bug — fine for dev/test; worth revisiting
# with a pooled prod config later if this becomes a bottleneck.
engine = create_async_engine(
    settings.DATABASE_URL, echo=False, poolclass=NullPool
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency: yields a DB session per-request, closes it after."""
    async with AsyncSessionLocal() as session:
        yield session


# --- Sync engine for Celery worker tasks ---
# Celery's default prefork worker model runs tasks as plain synchronous
# Python, not inside an asyncio event loop, so tasks use a separate sync
# engine/session rather than trying to bridge into the async one.
sync_engine = create_engine(settings.DATABASE_URL_SYNC, pool_pre_ping=True)
SyncSessionLocal = sessionmaker(bind=sync_engine, expire_on_commit=False)
