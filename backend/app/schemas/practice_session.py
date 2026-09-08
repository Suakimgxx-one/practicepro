import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class PracticeSessionStart(BaseModel):
    user_id: uuid.UUID
    piece_id: uuid.UUID
    focus_section: str | None = Field(default=None, max_length=255)
    session_goal: str | None = Field(default=None, max_length=255)
    target_tempo_bpm: int | None = Field(default=None, ge=1, le=400)


class PracticeSessionFinish(BaseModel):
    reflection_notes: str | None = None
    self_rating: int | None = Field(default=None, ge=1, le=5)


class PracticeSessionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: uuid.UUID
    piece_id: uuid.UUID
    focus_section: str | None
    session_goal: str | None
    target_tempo_bpm: int | None
    started_at: datetime
    ended_at: datetime | None
    duration_seconds: int | None
    reflection_notes: str | None
    self_rating: int | None
    created_at: datetime
