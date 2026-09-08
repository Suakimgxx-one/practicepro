import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Folder(Base):
    """
    A user-created group of pieces (e.g. "Audition Repertoire",
    "Orchestra Music"). A piece belongs to at most one folder for now
    (see Piece.folder_id) — many-to-many would need a join table,
    which is a reasonable later extension but not needed for the
    first version.
    """

    __tablename__ = "folders"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    # Simple named color (e.g. "violet", "emerald") rather than a hex
    # value — keeps the frontend's palette consistent and avoids users
    # picking colors that clash with the dark theme.
    color: Mapped[str] = mapped_column(String(20), nullable=False, default="violet")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    user: Mapped["User"] = relationship(back_populates="folders")
    pieces: Mapped[list["Piece"]] = relationship(back_populates="folder")
