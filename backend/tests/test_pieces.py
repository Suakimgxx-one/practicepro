import io
import uuid

import numpy as np
import pytest
import soundfile as sf


def _make_wav_bytes(
    freqs: list[float] = [261.63, 329.63, 392.00, 523.25],
    note_duration: float = 0.4,
    sample_rate: int = 16000,
) -> bytes:
    parts = []
    for freq in freqs:
        t = np.linspace(0, note_duration, int(sample_rate * note_duration), endpoint=False)
        parts.append(0.2 * np.sin(2 * np.pi * freq * t))
    waveform = np.concatenate(parts)
    buffer = io.BytesIO()
    sf.write(buffer, waveform, sample_rate, format="WAV")
    buffer.seek(0)
    return buffer.read()


async def _make_user(client) -> str:
    email = f"test-{uuid.uuid4().hex[:8]}@example.com"
    response = await client.post("/api/v1/users", json={"email": email})
    return response.json()["id"]


async def _make_ready_recording(
    client, user_id: str, recording_type: str, piece_id: str | None = None
) -> str:
    payload = {"user_id": user_id, "type": recording_type, "source": "upload"}
    if piece_id is not None:
        payload["piece_id"] = piece_id
    create_resp = await client.post("/api/v1/recordings", json=payload)
    recording_id = create_resp.json()["id"]
    upload_resp = await client.post(
        f"/api/v1/recordings/{recording_id}/upload",
        files={"file": ("test.wav", _make_wav_bytes(), "audio/wav")},
    )
    assert upload_resp.status_code == 200
    return recording_id


@pytest.mark.asyncio
async def test_create_piece(client):
    user_id = await _make_user(client)
    response = await client.post("/api/v1/pieces", json={"user_id": user_id, "title": "Mozart Flute Concerto No. 1"})
    assert response.status_code == 201
    body = response.json()
    assert body["title"] == "Mozart Flute Concerto No. 1"
    assert body["reference_recording_id"] is None


@pytest.mark.asyncio
async def test_list_pieces_for_user(client):
    user_id = await _make_user(client)
    await client.post("/api/v1/pieces", json={"user_id": user_id, "title": "Piece A"})
    await client.post("/api/v1/pieces", json={"user_id": user_id, "title": "Piece B"})
    response = await client.get("/api/v1/pieces", params={"user_id": user_id})
    assert response.status_code == 200
    assert len(response.json()) == 2


@pytest.mark.asyncio
async def test_reference_recording_auto_attaches_to_piece(client):
    """Creating a reference-type recording tagged with piece_id should
    automatically set that piece's reference_recording_id — no separate
    'attach reference' call needed."""
    user_id = await _make_user(client)
    piece_resp = await client.post("/api/v1/pieces", json={"user_id": user_id, "title": "Test Piece"})
    piece_id = piece_resp.json()["id"]

    reference_id = await _make_ready_recording(client, user_id, "reference", piece_id=piece_id)

    check = await client.get(f"/api/v1/pieces/{piece_id}")
    body = check.json()
    assert body["reference_recording_id"] == reference_id
    assert body["reference_recording"]["id"] == reference_id


@pytest.mark.asyncio
async def test_piece_detail_not_found(client):
    response = await client.get(f"/api/v1/pieces/{uuid.uuid4()}")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_piece_progress_reflects_completed_practice_attempts(client):
    """
    The real end-to-end test: create a piece, attach a reference,
    log two practice attempts against it, run analysis on both, and
    confirm the piece's progress list shows both completed attempts
    in chronological order with real headline stats — this is exactly
    what a 'see my progress over time' view needs.
    """
    user_id = await _make_user(client)
    piece_resp = await client.post("/api/v1/pieces", json={"user_id": user_id, "title": "Progress Test Piece"})
    piece_id = piece_resp.json()["id"]

    reference_id = await _make_ready_recording(client, user_id, "reference", piece_id=piece_id)
    attempt_1_id = await _make_ready_recording(client, user_id, "student", piece_id=piece_id)
    attempt_2_id = await _make_ready_recording(client, user_id, "student", piece_id=piece_id)

    session_1 = await client.post(
        "/api/v1/analysis-sessions",
        json={"user_id": user_id, "reference_recording_id": reference_id, "student_recording_id": attempt_1_id},
    )
    session_2 = await client.post(
        "/api/v1/analysis-sessions",
        json={"user_id": user_id, "reference_recording_id": reference_id, "student_recording_id": attempt_2_id},
    )
    assert session_1.json()["status"] == "complete"
    assert session_2.json()["status"] == "complete"

    detail = await client.get(f"/api/v1/pieces/{piece_id}")
    body = detail.json()

    assert len(body["attempts"]) == 2
    assert len(body["progress"]) == 2
    # Chronological order — first attempt's session should come first.
    assert body["progress"][0]["session_id"] == session_1.json()["id"]
    assert body["progress"][1]["session_id"] == session_2.json()["id"]
    # Real headline stats should be present, not null placeholders.
    assert body["progress"][0]["mean_absolute_cents_deviation"] is not None
