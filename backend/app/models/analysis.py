import enum
import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class SessionStatus(str, enum.Enum):
    PENDING = "pending"
    ALIGNING = "aligning"
    ANALYZING = "analyzing"
    COMPLETE = "complete"
    FAILED = "failed"


class AnalysisCategory(str, enum.Enum):
    PITCH = "pitch"
    RHYTHM = "rhythm"
    TEMPO = "tempo"
    DYNAMICS = "dynamics"


class AnalysisSession(Base):
    __tablename__ = "analysis_sessions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    reference_recording_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("recordings.id"), nullable=False)
    student_recording_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("recordings.id"), nullable=False)
    status: Mapped[SessionStatus] = mapped_column(
        Enum(SessionStatus, values_callable=lambda enum_cls: [e.value for e in enum_cls]),
        default=SessionStatus.PENDING,
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    user: Mapped["User"] = relationship(back_populates="analysis_sessions")
    results: Mapped[list["AnalysisResult"]] = relationship(back_populates="session")
    feedback_items: Mapped[list["Feedback"]] = relationship(back_populates="session")


class AnalysisResult(Base):
    __tablename__ = "analysis_results"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("analysis_sessions.id"), nullable=False)
    category: Mapped[AnalysisCategory] = mapped_column(
        Enum(AnalysisCategory, values_callable=lambda enum_cls: [e.value for e in enum_cls]),
        nullable=False,
    )
    data: Mapped[dict] = mapped_column(JSONB, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    session: Mapped["AnalysisSession"] = relationship(back_populates="results")
