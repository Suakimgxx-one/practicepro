import uuid

from fastapi import APIRouter, status

from app.api.deps import DBSession, PaginationParams
from app.schemas.recording import RecordingCreate, RecordingRead
from app.services import recording_service

router = APIRouter(prefix="/recordings", tags=["recordings"])


@router.post("", response_model=RecordingRead, status_code=status.HTTP_201_CREATED)
async def create_recording(payload: RecordingCreate, db: DBSession) -> RecordingRead:
    """
    Registers recording metadata. Does NOT accept audio bytes or trigger
    YouTube download — this just creates the row with status=PENDING.
    Milestone 3 adds the upload endpoint; Milestone 4 adds the YouTube
    ingestion job. Both will transition this row's status forward.
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
