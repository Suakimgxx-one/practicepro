import uuid

from fastapi import APIRouter, File, UploadFile, status

from app.api.deps import DBSession, PaginationParams
from app.schemas.recording import RecordingCreate, RecordingRead
from app.services import recording_service

router = APIRouter(prefix="/recordings", tags=["recordings"])


@router.post("", response_model=RecordingRead, status_code=status.HTTP_201_CREATED)
async def create_recording(payload: RecordingCreate, db: DBSession) -> RecordingRead:
    """
    Registers recording metadata. For source=upload, the row is created
    with status=pending and waits for the /upload endpoint. For
    source=youtube, creation automatically enqueues a background job
    (Celery) that downloads, validates, and transitions the row through
    processing -> ready/failed.
    """
    return await recording_service.create_recording(db, payload)


@router.get("/{recording_id}", response_model=RecordingRead)
async def get_recording(recording_id: uuid.UUID, db: DBSession) -> RecordingRead:
    return await recording_service.get_recording(db, recording_id)


@router.get("", response_model=list[RecordingRead])
async def list_recordings(
    db: DBSession,
    pagination: PaginationParams,
    user_id: uuid.UUID,
) -> list[RecordingRead]:
    return await recording_service.list_recordings_for_user(
        db, user_id, pagination.limit, pagination.offset
    )


@router.post("/{recording_id}/upload", response_model=RecordingRead)
async def upload_recording_audio(
    recording_id: uuid.UUID,
    db: DBSession,
    file: UploadFile = File(...),
) -> RecordingRead:
    """
    Accepts a multipart audio file for a recording created with
    source=upload. Validates file type, size, and actual decodability;
    on success the recording transitions to status=ready.
    """
    recording = await recording_service.get_recording(db, recording_id)
    return await recording_service.process_upload(db, recording, file)
