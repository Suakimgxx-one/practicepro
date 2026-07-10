import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict

from app.models.analysis import AnalysisCategory, SessionStatus


class AnalysisSessionCreate(BaseModel):
    reference_recording_id: uuid.UUID
    student_recording_id: uuid.UUID


class AnalysisSessionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: uuid.UUID
    reference_recording_id: uuid.UUID
    student_recording_id: uuid.UUID
    status: SessionStatus
    created_at: datetime


class AnalysisResultRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    session_id: uuid.UUID
    category: AnalysisCategory
    data: dict[str, Any]
    created_at: datetime
