import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Piece(Base):
    __tablename__ = "pieces"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    # Optional metadata — all nullable so existing pieces (created
    # before these fields existed) remain valid, and so the "quick add"
    # flow can stay a single title field.
    composer: Mapped[str | None] = mapped_column(String(255), nullable=True)
    instrument: Mapped[str | None] = mapped_column(String(100), nullable=True)
    folder_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("folders.id"), nullable=True)
    reference_recording_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("recordings.id"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    user: Mapped["User"] = relationship(back_populates="pieces")
    folder: Mapped["Folder | None"] = relationship(back_populates="pieces")
    reference_recording: Mapped["Recording | None"] = relationship(
        foreign_keys=[reference_recording_id]
    )
    # Practice attempts — student-type recordings tagged with this
    # piece. Filtered to type == 'student' because the reference
    # recording is ALSO tagged with this piece's id (that's how
    # auto-attachment works — see recording_service.create_recording),
    # so without this filter "attempts" would incorrectly include the
    # reference recording itself. viewonly=True: this is a derived,
    # filtered view of the relationship, not its writable side.
    attempts: Mapped[list["Recording"]] = relationship(
        primaryjoin="and_(Recording.piece_id==Piece.id, Recording.type=='student')",
        viewonly=True,
    )
    practice_sessions: Mapped[list["PracticeSession"]] = relationship(back_populates="piece")
