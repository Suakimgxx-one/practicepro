import enum
import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, Float, ForeignKey, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class RecordingType(str, enum.Enum):
    REFERENCE = "reference"
    STUDENT = "student"


class RecordingSource(str, enum.Enum):
    YOUTUBE = "youtube"
    UPLOAD = "upload"


class RecordingStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    READY = "ready"
    FAILED = "failed"


class Recording(Base):
    __tablename__ = "recordings"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    # Nullable: recordings created before the Pieces feature existed
    # (or a one-off comparison not attached to any piece) are still
    # valid rows.
    piece_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("pieces.id"), nullable=True)

    type: Mapped[RecordingType] = mapped_column(
        Enum(RecordingType, values_callable=lambda enum_cls: [e.value for e in enum_cls]),
        nullable=False,
    )
    source: Mapped[RecordingSource] = mapped_column(
        Enum(RecordingSource, values_callable=lambda enum_cls: [e.value for e in enum_cls]),
        nullable=False,
    )
    source_url: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    storage_path: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    duration_seconds: Mapped[float | None] = mapped_column(Float, nullable=True)
    status: Mapped[RecordingStatus] = mapped_column(
        Enum(RecordingStatus, values_callable=lambda enum_cls: [e.value for e in enum_cls]),
        default=RecordingStatus.PENDING,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    user: Mapped["User"] = relationship(back_populates="recordings")
    # No back_populates: Piece.attempts is a filtered (viewonly) view of
    # this same foreign key, not a symmetric writable relationship — see
    # the comment on Piece.attempts for why the filter is needed.
    piece: Mapped["Piece | None"] = relationship(foreign_keys=[piece_id])
