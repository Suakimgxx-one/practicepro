import pytest
from httpx import ASGITransport, AsyncClient

from app.db.session import AsyncSessionLocal
from app.main import app
from worker.celery_app import celery_app


@pytest.fixture(scope="session", autouse=True)
def _celery_eager_mode():
    """
    Forces Celery tasks to execute synchronously, in-process, instead of
    being pushed to Redis and picked up by the real worker container.
    Without this, tests that create a youtube-source recording would
    enqueue a real task that the actual worker process would then try to
    run — hitting real YouTube over the network from a background
    process we have no hook into from pytest. Eager mode keeps task
    execution (and any mocking of it) inside this test process.
    """
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
