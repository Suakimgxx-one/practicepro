import uuid
from pathlib import Path
from unittest.mock import patch

import numpy as np
import pytest
import soundfile as sf


def _write_fake_wav(path: Path, duration_seconds: float = 0.75, sample_rate: int = 16000) -> None:
    t = np.linspace(0, duration_seconds, int(sample_rate * duration_seconds), endpoint=False)
    waveform = 0.1 * np.sin(2 * np.pi * 440 * t)
    path.parent.mkdir(parents=True, exist_ok=True)
    sf.write(str(path), waveform, sample_rate)


async def _make_user(client) -> str:
    email = f"test-{uuid.uuid4().hex[:8]}@example.com"
    response = await client.post("/api/v1/users", json={"email": email})
    return response.json()["id"]


@pytest.mark.asyncio
async def test_youtube_recording_processes_successfully(client, tmp_path):
    """
    End-to-end: creating a youtube-source recording auto-enqueues the
    ingestion task (run synchronously here via Celery eager mode); with
    the actual download mocked out, we confirm the recording correctly
    transitions all the way to ready with a real extracted duration.
    """
    fake_audio = tmp_path / "fake_original.wav"
    _write_fake_wav(fake_audio, duration_seconds=0.75)

    user_id = await _make_user(client)

    with patch("worker.tasks.ingest._download_audio", return_value=fake_audio):
        response = await client.post(
            "/api/v1/recordings",
            json={
                "user_id": user_id,
                "type": "reference",
                "source": "youtube",
                "source_url": "https://youtube.com/watch?v=fake123",
            },
        )

    assert response.status_code == 201
    recording_id = response.json()["id"]

    check = await client.get(f"/api/v1/recordings/{recording_id}")
    body = check.json()
    assert body["status"] == "ready"
    assert body["duration_seconds"] == pytest.approx(0.75, abs=0.05)
    assert body["storage_path"] is not None


@pytest.mark.asyncio
async def test_youtube_recording_marks_failed_on_download_error(client):
    """A yt-dlp failure (private video, geo-block, network error, etc.)
    should leave the recording in a clear failed state, not stuck
    pending/processing forever."""
    user_id = await _make_user(client)

    with patch(
        "worker.tasks.ingest._download_audio",
        side_effect=RuntimeError("Video unavailable"),
    ):
        response = await client.post(
            "/api/v1/recordings",
            json={
                "user_id": user_id,
                "type": "reference",
                "source": "youtube",
                "source_url": "https://youtube.com/watch?v=badvideo",
            },
        )

    recording_id = response.json()["id"]
    check = await client.get(f"/api/v1/recordings/{recording_id}")
    assert check.json()["status"] == "failed"


@pytest.mark.asyncio
async def test_youtube_recording_marks_failed_on_invalid_audio(client, tmp_path):
    """Download 'succeeds' but produces a file that isn't real audio —
    should still fail cleanly via the same validation path uploads use."""
    fake_bad_file = tmp_path / "not_really_audio.wav"
    fake_bad_file.write_bytes(b"garbage, not audio" * 50)

    user_id = await _make_user(client)

    with patch("worker.tasks.ingest._download_audio", return_value=fake_bad_file):
        response = await client.post(
            "/api/v1/recordings",
            json={
                "user_id": user_id,
                "type": "reference",
                "source": "youtube",
                "source_url": "https://youtube.com/watch?v=corrupt",
            },
        )

    recording_id = response.json()["id"]
    check = await client.get(f"/api/v1/recordings/{recording_id}")
    assert check.json()["status"] == "failed"


@pytest.mark.asyncio
async def test_upload_source_recording_does_not_trigger_youtube_task(client):
    """Sanity check: creating an upload-source recording must NOT enqueue
    the youtube task — if it did, this test would try a real network
    call since we're not patching anything here."""
    user_id = await _make_user(client)
    response = await client.post(
        "/api/v1/recordings",
        json={"user_id": user_id, "type": "student", "source": "upload"},
    )
    assert response.status_code == 201
    assert response.json()["status"] == "pending"
