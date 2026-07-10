import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.analysis import AnalysisCategory


class FeedbackRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    session_id: uuid.UUID
    category: AnalysisCategory
    text: str
    timestamp_reference: float | None
    created_at: datetime
