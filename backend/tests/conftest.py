import pytest
from httpx import ASGITransport, AsyncClient

from app.db.session import AsyncSessionLocal
from app.main import app


@pytest.fixture
async def client():
    """
    Async HTTP client wired directly to the FastAPI app in-process (no
    real network socket) via ASGITransport. Runs against the same DB
    the dev compose stack uses — see README for `pytest` invocation.
    """
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.fixture
async def db_session():
    async with AsyncSessionLocal() as session:
        yield session
