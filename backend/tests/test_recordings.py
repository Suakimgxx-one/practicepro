import uuid

import pytest


async def _make_user(client) -> str:
    email = f"test-{uuid.uuid4().hex[:8]}@example.com"
    response = await client.post("/api/v1/users", json={"email": email})
    return response.json()["id"]


@pytest.mark.asyncio
async def test_create_recording_upload_source(client):
    user_id = await _make_user(client)
    response = await client.post(
        "/api/v1/recordings",
        json={"user_id": user_id, "type": "student", "source": "upload"},
    )
    assert response.status_code == 201
    body = response.json()
    assert body["status"] == "pending"
    assert body["type"] == "student"


@pytest.mark.asyncio
async def test_create_recording_youtube_requires_url(client):
    user_id = await _make_user(client)
    response = await client.post(
        "/api/v1/recordings",
        json={"user_id": user_id, "type": "reference", "source": "youtube"},
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_get_recording_not_found(client):
    response = await client.get(f"/api/v1/recordings/{uuid.uuid4()}")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_list_recordings_for_user(client):
    user_id = await _make_user(client)
    await client.post(
        "/api/v1/recordings",
        json={"user_id": user_id, "type": "student", "source": "upload"},
    )
    response = await client.get("/api/v1/recordings", params={"user_id": user_id})
    assert response.status_code == 200
    assert len(response.json()) == 1
