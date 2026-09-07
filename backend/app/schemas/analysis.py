import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict

from app.models.analysis import AnalysisCategory, SessionStatus
from app.schemas.feedback import FeedbackRead


class AnalysisSessionCreate(BaseModel):
    # NOTE: same no-auth tradeoff as RecordingCreate — user_id is passed
    # explicitly since there's no session/auth layer yet.
    user_id: uuid.UUID
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


class AnalysisSessionDetail(AnalysisSessionRead):
    """
    Full session view including nested results and feedback — what the
    frontend polls to render pitch/rhythm/tempo/dynamics charts and
    coaching text once a session reaches status=complete.
    """

    results: list[AnalysisResultRead] = []
    feedback: list[FeedbackRead] = []
