import uuid

import pytest


@pytest.mark.asyncio
async def test_create_user(client):
    email = f"test-{uuid.uuid4().hex[:8]}@example.com"
    response = await client.post("/api/v1/users", json={"email": email})
    assert response.status_code == 201
    body = response.json()
    assert body["email"] == email
    assert "id" in body


@pytest.mark.asyncio
async def test_create_user_idempotent_on_email(client):
    email = f"test-{uuid.uuid4().hex[:8]}@example.com"
    first = await client.post("/api/v1/users", json={"email": email})
    second = await client.post("/api/v1/users", json={"email": email})
    assert first.json()["id"] == second.json()["id"]


@pytest.mark.asyncio
async def test_get_user_not_found(client):
    response = await client.get(f"/api/v1/users/{uuid.uuid4()}")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_user(client):
    email = f"test-{uuid.uuid4().hex[:8]}@example.com"
    created = await client.post("/api/v1/users", json={"email": email})
    user_id = created.json()["id"]

    response = await client.get(f"/api/v1/users/{user_id}")
    assert response.status_code == 200
    assert response.json()["email"] == email
