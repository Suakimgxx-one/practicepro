import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, Float, ForeignKey, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.analysis import AnalysisCategory


class Feedback(Base):
    __tablename__ = "feedback"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("analysis_sessions.id"), nullable=False)
    category: Mapped[AnalysisCategory] = mapped_column(
        Enum(AnalysisCategory, values_callable=lambda enum_cls: [e.value for e in enum_cls]),
        nullable=False,
    )
    text: Mapped[str] = mapped_column(Text, nullable=False)
    timestamp_reference: Mapped[float | None] = mapped_column(Float, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    session: Mapped["AnalysisSession"] = relationship(back_populates="feedback_items")
