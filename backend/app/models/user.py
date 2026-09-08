import uuid
from datetime import datetime

from sqlalchemy import DateTime, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    recordings: Mapped[list["Recording"]] = relationship(back_populates="user")
    analysis_sessions: Mapped[list["AnalysisSession"]] = relationship(back_populates="user")
    pieces: Mapped[list["Piece"]] = relationship(back_populates="user")
    folders: Mapped[list["Folder"]] = relationship(back_populates="user")
    practice_sessions: Mapped[list["PracticeSession"]] = relationship(back_populates="user")
