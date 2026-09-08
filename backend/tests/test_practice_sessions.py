import uuid

import pytest


async def _make_user(client) -> str:
    email = f"test-{uuid.uuid4().hex[:8]}@example.com"
    response = await client.post("/api/v1/users", json={"email": email})
    return response.json()["id"]


async def _make_piece(client, user_id: str) -> str:
    response = await client.post("/api/v1/pieces", json={"user_id": user_id, "title": "Test Piece"})
    return response.json()["id"]


@pytest.mark.asyncio
async def test_start_practice_session(client):
    user_id = await _make_user(client)
    piece_id = await _make_piece(client, user_id)

    response = await client.post(
        "/api/v1/practice-sessions",
        json={"user_id": user_id, "piece_id": piece_id, "session_goal": "Clean up measure 32", "target_tempo_bpm": 96},
    )
    assert response.status_code == 201
    body = response.json()
    assert body["ended_at"] is None
    assert body["duration_seconds"] is None
    assert body["session_goal"] == "Clean up measure 32"


@pytest.mark.asyncio
async def test_finish_practice_session_computes_duration(client):
    user_id = await _make_user(client)
    piece_id = await _make_piece(client, user_id)

    start_resp = await client.post(
        "/api/v1/practice-sessions", json={"user_id": user_id, "piece_id": piece_id}
    )
    session_id = start_resp.json()["id"]

    finish_resp = await client.patch(
        f"/api/v1/practice-sessions/{session_id}/finish",
        json={"reflection_notes": "Intonation felt more stable today.", "self_rating": 4},
    )
    assert finish_resp.status_code == 200
    body = finish_resp.json()
    assert body["ended_at"] is not None
    assert body["duration_seconds"] is not None
    assert body["duration_seconds"] >= 0
    assert body["self_rating"] == 4


@pytest.mark.asyncio
async def test_self_rating_out_of_range_is_rejected(client):
    user_id = await _make_user(client)
    piece_id = await _make_piece(client, user_id)
    start_resp = await client.post(
        "/api/v1/practice-sessions", json={"user_id": user_id, "piece_id": piece_id}
    )
    session_id = start_resp.json()["id"]

    response = await client.patch(
        f"/api/v1/practice-sessions/{session_id}/finish", json={"self_rating": 9}
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_piece_detail_reports_total_practice_time(client):
    user_id = await _make_user(client)
    piece_id = await _make_piece(client, user_id)

    for _ in range(2):
        start_resp = await client.post(
            "/api/v1/practice-sessions", json={"user_id": user_id, "piece_id": piece_id}
        )
        session_id = start_resp.json()["id"]
        await client.patch(f"/api/v1/practice-sessions/{session_id}/finish", json={})

    detail = await client.get(f"/api/v1/pieces/{piece_id}")
    body = detail.json()
    assert len(body["practice_sessions"]) == 2
    assert body["total_practice_seconds"] >= 0


@pytest.mark.asyncio
async def test_list_practice_sessions_for_piece(client):
    user_id = await _make_user(client)
    piece_id = await _make_piece(client, user_id)
    await client.post("/api/v1/practice-sessions", json={"user_id": user_id, "piece_id": piece_id})

    response = await client.get("/api/v1/practice-sessions", params={"piece_id": piece_id})
    assert response.status_code == 200
    assert len(response.json()) == 1


@pytest.mark.asyncio
async def test_list_practice_sessions_for_user_across_pieces(client):
    user_id = await _make_user(client)
    piece_1 = await _make_piece(client, user_id)
    piece_2 = await _make_piece(client, user_id)
    await client.post("/api/v1/practice-sessions", json={"user_id": user_id, "piece_id": piece_1})
    await client.post("/api/v1/practice-sessions", json={"user_id": user_id, "piece_id": piece_2})

    response = await client.get("/api/v1/practice-sessions", params={"user_id": user_id})
    assert response.status_code == 200
    assert len(response.json()) == 2


@pytest.mark.asyncio
async def test_list_practice_sessions_requires_a_filter(client):
    response = await client.get("/api/v1/practice-sessions")
    assert response.status_code == 422
