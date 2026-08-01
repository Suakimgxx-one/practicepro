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


@celery_app.task(name="ingest.process_youtube_recording", bind=True, max_retries=2)
def process_youtube_recording(self, recording_id: str) -> None:
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
