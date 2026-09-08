import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class PracticeSession(Base):
    """
    A single timed practice session against a piece. started_at is set
    at creation; ended_at and duration_seconds are filled in when the
    session is finished (see PATCH /practice-sessions/{id}/finish).
    A session with ended_at IS NULL is still in progress — that's how
    the frontend distinguishes an active timer from history.
    """

    __tablename__ = "practice_sessions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    piece_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("pieces.id"), nullable=False)

    focus_section: Mapped[str | None] = mapped_column(String(255), nullable=True)
    session_goal: Mapped[str | None] = mapped_column(String(255), nullable=True)
    target_tempo_bpm: Mapped[int | None] = mapped_column(Integer, nullable=True)

    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    ended_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    duration_seconds: Mapped[int | None] = mapped_column(Integer, nullable=True)

    reflection_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    # 1-5 self-rating, filled in at finish time — validated in the
    # Pydantic schema, not at the DB level, since this is a UI-facing
    # scale rather than a hard data-integrity constraint.
    self_rating: Mapped[int | None] = mapped_column(Integer, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    user: Mapped["User"] = relationship(back_populates="practice_sessions")
    piece: Mapped["Piece"] = relationship(back_populates="practice_sessions")
