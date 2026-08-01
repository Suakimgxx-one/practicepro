import uuid

from fastapi import UploadFile
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import InvalidAudioError, NotFoundError, RecordingConflictError
from app.models.recording import Recording, RecordingSource, RecordingStatus
from app.schemas.recording import RecordingCreate
from app.services import audio_service, storage_service


async def create_recording(db: AsyncSession, payload: RecordingCreate) -> Recording:
    recording = Recording(
        user_id=payload.user_id,
        type=payload.type,
        source=payload.source,
        source_url=payload.source_url,
    )
    db.add(recording)
    await db.commit()
    await db.refresh(recording)

    if recording.source == RecordingSource.YOUTUBE:
        from worker.tasks.ingest import process_youtube_recording

        process_youtube_recording.delay(str(recording.id))

    return recording


async def get_recording(db: AsyncSession, recording_id: uuid.UUID) -> Recording:
    recording = await db.get(Recording, recording_id)
    if recording is None:
        raise NotFoundError("Recording", str(recording_id))
    return recording


async def list_recordings_for_user(
    db: AsyncSession, user_id: uuid.UUID, limit: int, offset: int
) -> list[Recording]:
    result = await db.execute(
        select(Recording)
        .where(Recording.user_id == user_id)
        .order_by(Recording.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    return list(result.scalars().all())


async def process_upload(
    db: AsyncSession, recording: Recording, upload_file: UploadFile
) -> Recording:
    if recording.status == RecordingStatus.READY:
        raise RecordingConflictError(str(recording.id))

    destination = await storage_service.save_upload(recording.id, upload_file)

    try:
        duration = await audio_service.probe_duration(destination)
    except InvalidAudioError:
        storage_service.delete_file(destination)
        recording.status = RecordingStatus.FAILED
        await db.commit()
        await db.refresh(recording)
        raise

    recording.storage_path = str(destination)
    recording.duration_seconds = duration
    recording.status = RecordingStatus.READY
    await db.commit()
    await db.refresh(recording)
    return recording
