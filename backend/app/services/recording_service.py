import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError
from app.models.recording import Recording
from app.schemas.recording import RecordingCreate


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
