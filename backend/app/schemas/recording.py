import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.models.recording import RecordingSource, RecordingStatus, RecordingType


class RecordingCreate(BaseModel):
    """
    Request body for registering a new recording. Note: this only creates
    the DB row / metadata. The actual audio bytes (upload) or the YouTube
    ingestion job are handled by dedicated endpoints in Milestone 3 & 4 —
    this schema exists now so the API shape is settled early.
    """

    # NOTE: no auth system exists yet, so user_id is passed explicitly here.
    # Once auth lands, this will be dropped in favor of an authenticated
    # `current_user` dependency and this field will be removed from the
    # public request schema.
    user_id: uuid.UUID
    type: RecordingType
    source: RecordingSource
    source_url: str | None = Field(default=None, max_length=1024)

    @model_validator(mode="after")
    def require_url_for_youtube(self) -> "RecordingCreate":
        if self.source == RecordingSource.YOUTUBE and not self.source_url:
            raise ValueError("source_url is required when source is 'youtube'")
        return self


class RecordingRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: uuid.UUID
    type: RecordingType
    source: RecordingSource
    source_url: str | None
    storage_path: str | None
    duration_seconds: float | None
    status: RecordingStatus
    created_at: datetime
