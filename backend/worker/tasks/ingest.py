import logging
import time
from pathlib import Path

import yt_dlp

from app.core.config import settings
from app.db.session import SyncSessionLocal
from app.models.recording import Recording, RecordingStatus
from app.services.audio_service import probe_duration_sync
from worker.celery_app import celery_app

logger = logging.getLogger(__name__)

# Up to 2 retries (3 attempts total) on a short backoff. This used to
# be implemented with Celery's task-level self.retry(), which re-queues
# the ENTIRE task via the broker — that works fine in real deployment,
# but Celery's "eager" mode (used throughout our test suite, via
# task_always_eager=True) doesn't actually loop and retry inline the
# way it might seem to; it raises a Retry exception that propagates
# all the way out of .delay(), which crashes the calling HTTP request
# in tests. A plain local loop avoids that entirely and behaves
# identically whether eager or not — this is the same pattern already
# used for the LLM feedback call in worker/tasks/analyze.py.
MAX_ATTEMPTS = 3
RETRY_BACKOFF_SECONDS = 2


def _download_audio(source_url: str, dest_dir: Path) -> Path:
    dest_dir.mkdir(parents=True, exist_ok=True)
    output_template = str(dest_dir / "original.%(ext)s")

    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": output_template,
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "wav",
            }
        ],
        "quiet": True,
        "no_warnings": True,
        "noplaylist": True,
        "extractor_args": {
            "youtube": {
                "player_client": ["android", "ios", "web"],
            }
        },
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([source_url])

    result = dest_dir / "original.wav"
    if not result.exists():
        raise FileNotFoundError(f"Expected downloaded audio at {result}, but it wasn't created")
    return result


@celery_app.task(name="ingest.process_youtube_recording")
def process_youtube_recording(recording_id: str) -> None:
    session = SyncSessionLocal()
    try:
        recording = session.get(Recording, recording_id)
        if recording is None:
            logger.error("Recording %s not found, aborting ingestion", recording_id)
            return

        recording.status = RecordingStatus.PROCESSING
        session.commit()

        dest_dir = Path(settings.LOCAL_STORAGE_PATH) / str(recording.id)

        audio_path: Path | None = None
        duration: float | None = None
        last_error: Exception | None = None

        for attempt in range(MAX_ATTEMPTS):
            try:
                audio_path = _download_audio(recording.source_url, dest_dir)
                duration = probe_duration_sync(str(audio_path))
                break
            except Exception as exc:
                last_error = exc
                logger.warning(
                    "YouTube ingestion attempt %d/%d failed for recording %s: %s",
                    attempt + 1,
                    MAX_ATTEMPTS,
                    recording_id,
                    exc,
                )
                if attempt < MAX_ATTEMPTS - 1:
                    time.sleep(RETRY_BACKOFF_SECONDS * (attempt + 1))

        if audio_path is None or duration is None:
            logger.error(
                "YouTube ingestion failed for recording %s after %d attempts: %s",
                recording_id,
                MAX_ATTEMPTS,
                last_error,
            )
            recording.status = RecordingStatus.FAILED
            session.commit()
            return

        recording.storage_path = str(audio_path)
        recording.duration_seconds = duration
        recording.status = RecordingStatus.READY
        session.commit()
    finally:
        session.close()
