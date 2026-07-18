import logging
from pathlib import Path

import yt_dlp

from app.core.config import settings
from app.db.session import SyncSessionLocal
from app.models.recording import Recording, RecordingStatus
from app.services.audio_service import probe_duration_sync
from worker.celery_app import celery_app

logger = logging.getLogger(__name__)


def _download_audio(source_url: str, dest_dir: Path) -> Path:
    """
    Downloads and extracts audio from a YouTube URL via yt-dlp, converting
    to WAV so it flows through the exact same validation/duration path as
    a direct upload (one code path for "is this real audio", regardless
    of where the bytes came from).

    Deliberately isolated from Celery/DB concerns — this function takes a
    URL and a directory, returns a path. That makes it trivially mockable
    in tests without needing a real network call or a running worker.
    """
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
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([source_url])

    result = dest_dir / "original.wav"
    if not result.exists():
        raise FileNotFoundError(f"Expected downloaded audio at {result}, but it wasn't created")
    return result


@celery_app.task(name="ingest.process_youtube_recording", bind=True, max_retries=2)
def process_youtube_recording(self, recording_id: str) -> None:
    """
    Full lifecycle for a YouTube-sourced recording: pending -> processing
    -> (ready | failed). Uses a plain sync DB session since Celery's
    default prefork worker runs tasks outside any asyncio event loop.
    """
    session = SyncSessionLocal()
    try:
        recording = session.get(Recording, recording_id)
        if recording is None:
            logger.error("Recording %s not found, aborting ingestion", recording_id)
            return

        recording.status = RecordingStatus.PROCESSING
        session.commit()

        dest_dir = Path(settings.LOCAL_STORAGE_PATH) / str(recording.id)

        try:
            audio_path = _download_audio(recording.source_url, dest_dir)
            duration = probe_duration_sync(str(audio_path))
        except Exception:
            # Covers yt-dlp failures (private/deleted/geo-blocked videos,
            # network errors) and audio validation failures alike — any
            # of these means the recording didn't make it to a usable
            # state, so it's marked failed rather than left stuck in
            # "processing" forever.
            logger.exception("YouTube ingestion failed for recording %s", recording_id)
            recording.status = RecordingStatus.FAILED
            session.commit()
            return

        recording.storage_path = str(audio_path)
        recording.duration_seconds = duration
        recording.status = RecordingStatus.READY
        session.commit()
    finally:
        session.close()
