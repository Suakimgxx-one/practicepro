import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.practice_session import PracticeSessionRead
from app.schemas.recording import RecordingRead


class PieceCreate(BaseModel):
    user_id: uuid.UUID
    title: str = Field(min_length=1, max_length=255)
    composer: str | None = Field(default=None, max_length=255)
    instrument: str | None = Field(default=None, max_length=100)
    folder_id: uuid.UUID | None = None


class PieceUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    composer: str | None = Field(default=None, max_length=255)
    instrument: str | None = Field(default=None, max_length=100)
    folder_id: uuid.UUID | None = None


class PieceRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: uuid.UUID
    title: str
    composer: str | None
    instrument: str | None
    folder_id: uuid.UUID | None
    reference_recording_id: uuid.UUID | None
    created_at: datetime


class PieceProgressPoint(BaseModel):
    session_id: uuid.UUID
    student_recording_id: uuid.UUID
    created_at: datetime
    mean_absolute_cents_deviation: float | None = None
    mean_absolute_timing_offset_seconds: float | None = None
    mean_tempo_ratio: float | None = None
    mean_absolute_loudness_difference_db: float | None = None


class PieceDetail(PieceRead):
    reference_recording: RecordingRead | None = None
    attempts: list[RecordingRead] = []
    progress: list[PieceProgressPoint] = []
    practice_sessions: list[PracticeSessionRead] = []
    total_practice_seconds: int = 0
