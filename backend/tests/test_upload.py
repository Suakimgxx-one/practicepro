import io
import uuid

import numpy as np
import pytest
import soundfile as sf


def _make_wav_bytes(duration_seconds: float = 0.5, sample_rate: int = 16000) -> bytes:
    t = np.linspace(0, duration_seconds, int(sample_rate * duration_seconds), endpoint=False)
    waveform = 0.1 * np.sin(2 * np.pi * 440 * t)
    buffer = io.BytesIO()
    sf.write(buffer, waveform, sample_rate, format="WAV")
    buffer.seek(0)
    return buffer.read()


async def _make_user_and_upload_recording(client) -> tuple[str, str]:
    email = f"test-{uuid.uuid4().hex[:8]}@example.com"
    user_resp = await client.post("/api/v1/users", json={"email": email})
    user_id = user_resp.json()["id"]
    recording_resp = await client.post(
        "/api/v1/recordings",
        json={"user_id": user_id, "type": "student", "source": "upload"},
    )
    return user_id, recording_resp.json()["id"]


@pytest.mark.asyncio
async def test_upload_valid_audio(client):
    _, recording_id = await _make_user_and_upload_recording(client)
    wav_bytes = _make_wav_bytes()
    response = await client.post(
        f"/api/v1/recordings/{recording_id}/upload",
        files={"file": ("test.wav", wav_bytes, "audio/wav")},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ready"
    assert body["storage_path"] is not None
    assert body["duration_seconds"] == pytest.approx(0.5, abs=0.05)


@pytest.mark.asyncio
async def test_upload_rejects_bad_extension(client):
    _, recording_id = await _make_user_and_upload_recording(client)
    response = await client.post(
        f"/api/v1/recordings/{recording_id}/upload",
        files={"file": ("test.txt", b"not audio", "text/plain")},
    )
    assert response.status_code == 415


@pytest.mark.asyncio
async def test_upload_rejects_corrupt_audio(client):
    _, recording_id = await _make_user_and_upload_recording(client)
    response = await client.post(
        f"/api/v1/recordings/{recording_id}/upload",
        files={"file": ("test.wav", b"this is not really a wav file" * 100, "audio/wav")},
    )
    assert response.status_code == 422
    check = await client.get(f"/api/v1/recordings/{recording_id}")
    assert check.json()["status"] == "failed"


@pytest.mark.asyncio
async def test_upload_rejects_when_already_ready(client):
    _, recording_id = await _make_user_and_upload_recording(client)
    wav_bytes = _make_wav_bytes()
    first = await client.post(
        f"/api/v1/recordings/{recording_id}/upload",
        files={"file": ("test.wav", wav_bytes, "audio/wav")},
    )
    assert first.status_code == 200
    second = await client.post(
        f"/api/v1/recordings/{recording_id}/upload",
        files={"file": ("test.wav", wav_bytes, "audio/wav")},
    )
    assert second.status_code == 409


@pytest.mark.asyncio
async def test_upload_to_nonexistent_recording(client):
    wav_bytes = _make_wav_bytes()
    response = await client.post(
        f"/api/v1/recordings/{uuid.uuid4()}/upload",
        files={"file": ("test.wav", wav_bytes, "audio/wav")},
    )
    assert response.status_code == 404
