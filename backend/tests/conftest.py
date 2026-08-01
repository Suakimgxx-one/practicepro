import pytest
from httpx import ASGITransport, AsyncClient

from app.db.session import AsyncSessionLocal
from app.main import app
from worker.celery_app import celery_app


@pytest.fixture(scope="session", autouse=True)
def _celery_eager_mode():
    celery_app.conf.update(task_always_eager=True, task_eager_propagates=True)


@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.fixture
async def db_session():
    async with AsyncSessionLocal() as session:
        yield session
