import uuid

import pytest


async def _make_user(client) -> str:
    email = f"test-{uuid.uuid4().hex[:8]}@example.com"
    response = await client.post("/api/v1/users", json={"email": email})
    return response.json()["id"]


@pytest.mark.asyncio
async def test_create_folder(client):
    user_id = await _make_user(client)
    response = await client.post(
        "/api/v1/folders", json={"user_id": user_id, "name": "Audition Repertoire", "color": "violet"}
    )
    assert response.status_code == 201
    body = response.json()
    assert body["name"] == "Audition Repertoire"
    assert body["piece_count"] == 0


@pytest.mark.asyncio
async def test_list_folders_includes_piece_counts(client):
    user_id = await _make_user(client)
    folder_resp = await client.post("/api/v1/folders", json={"user_id": user_id, "name": "Orchestra Music"})
    folder_id = folder_resp.json()["id"]

    await client.post("/api/v1/pieces", json={"user_id": user_id, "title": "Piece A", "folder_id": folder_id})
    await client.post("/api/v1/pieces", json={"user_id": user_id, "title": "Piece B", "folder_id": folder_id})
    await client.post("/api/v1/pieces", json={"user_id": user_id, "title": "Unfiled Piece"})

    response = await client.get("/api/v1/folders", params={"user_id": user_id})
    folders = response.json()
    assert len(folders) == 1
    assert folders[0]["piece_count"] == 2


@pytest.mark.asyncio
async def test_rename_folder(client):
    user_id = await _make_user(client)
    folder_resp = await client.post("/api/v1/folders", json={"user_id": user_id, "name": "Old Name"})
    folder_id = folder_resp.json()["id"]

    response = await client.patch(f"/api/v1/folders/{folder_id}", json={"name": "New Name"})
    assert response.status_code == 200
    assert response.json()["name"] == "New Name"


@pytest.mark.asyncio
async def test_delete_folder_unfiles_pieces_instead_of_deleting_them(client):
    user_id = await _make_user(client)
    folder_resp = await client.post("/api/v1/folders", json={"user_id": user_id, "name": "Temp Folder"})
    folder_id = folder_resp.json()["id"]

    piece_resp = await client.post(
        "/api/v1/pieces", json={"user_id": user_id, "title": "Orphaned Piece", "folder_id": folder_id}
    )
    piece_id = piece_resp.json()["id"]

    delete_resp = await client.delete(f"/api/v1/folders/{folder_id}")
    assert delete_resp.status_code == 204

    piece_check = await client.get(f"/api/v1/pieces/{piece_id}")
    assert piece_check.status_code == 200
    assert piece_check.json()["folder_id"] is None
