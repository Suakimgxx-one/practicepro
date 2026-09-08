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


async def _make_ready_recording(client, user_id: str, recording_type: str) -> str:
    create_resp = await client.post(
        "/api/v1/recordings",
        json={"user_id": user_id, "type": recording_type, "source": "upload"},
    )
    recording_id = create_resp.json()["id"]
    upload_resp = await client.post(
        f"/api/v1/recordings/{recording_id}/upload",
        files={"file": ("test.wav", _make_wav_bytes(), "audio/wav")},
    )
    assert upload_resp.status_code == 200
    assert upload_resp.json()["status"] == "ready"
    return recording_id


@pytest.mark.asyncio
async def test_analysis_session_completes_with_all_four_categories(client):
    user_id = await _make_user(client)
    reference_id = await _make_ready_recording(client, user_id, "reference")
    student_id = await _make_ready_recording(client, user_id, "student")

    response = await client.post(
        "/api/v1/analysis-sessions",
        json={"user_id": user_id, "reference_recording_id": reference_id, "student_recording_id": student_id},
    )
    assert response.status_code == 201
    session_id = response.json()["id"]

    check = await client.get(f"/api/v1/analysis-sessions/{session_id}")
    body = check.json()

    assert body["status"] == "complete"
    categories = {r["category"] for r in body["results"]}
    assert categories == {"pitch", "rhythm", "tempo", "dynamics"}

    pitch_result = next(r for r in body["results"] if r["category"] == "pitch")
    assert "mean_absolute_cents_deviation" in pitch_result["data"]
    assert "flagged_regions" in pitch_result["data"]


@pytest.mark.asyncio
async def test_analysis_session_fails_gracefully_when_recording_not_ready(client):
    user_id = await _make_user(client)
    pending_resp = await client.post(
        "/api/v1/recordings", json={"user_id": user_id, "type": "reference", "source": "upload"}
    )
    pending_id = pending_resp.json()["id"]
    ready_id = await _make_ready_recording(client, user_id, "student")

    response = await client.post(
        "/api/v1/analysis-sessions",
        json={"user_id": user_id, "reference_recording_id": pending_id, "student_recording_id": ready_id},
    )
    session_id = response.json()["id"]

    check = await client.get(f"/api/v1/analysis-sessions/{session_id}")
    assert check.json()["status"] == "failed"


@pytest.mark.asyncio
async def test_analysis_session_not_found(client):
    response = await client.get(f"/api/v1/analysis-sessions/{uuid.uuid4()}")
    assert response.status_code == 404
