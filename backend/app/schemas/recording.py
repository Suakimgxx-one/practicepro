import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.models.recording import RecordingSource, RecordingStatus, RecordingType


class RecordingCreate(BaseModel):
    user_id: uuid.UUID
    type: RecordingType
    source: RecordingSource
    source_url: str | None = Field(default=None, max_length=1024)
    # Optional: ties this recording to a Piece so it shows up in that
    # piece's practice history / progress view.
    piece_id: uuid.UUID | None = None

    @model_validator(mode="after")
    def require_url_for_youtube(self) -> "RecordingCreate":
        if self.source == RecordingSource.YOUTUBE and not self.source_url:
            raise ValueError("source_url is required when source is 'youtube'")
        return self


class RecordingRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: uuid.UUID
    piece_id: uuid.UUID | None
    type: RecordingType
    source: RecordingSource
    source_url: str | None
    storage_path: str | None
    duration_seconds: float | None
    status: RecordingStatus
    created_at: datetime
