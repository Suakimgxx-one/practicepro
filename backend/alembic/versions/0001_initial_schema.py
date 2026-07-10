"""initial schema

Revision ID: 0001
Revises:
Create Date: 2026-07-03
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("email", sa.String(255), nullable=False, unique=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    recording_type = postgresql.ENUM("reference", "student", name="recordingtype")
    recording_source = postgresql.ENUM("youtube", "upload", name="recordingsource")
    recording_status = postgresql.ENUM(
        "pending", "processing", "ready", "failed", name="recordingstatus"
    )

    op.create_table(
        "recordings",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("type", recording_type, nullable=False),
        sa.Column("source", recording_source, nullable=False),
        sa.Column("source_url", sa.String(1024), nullable=True),
        sa.Column("storage_path", sa.String(1024), nullable=True),
        sa.Column("duration_seconds", sa.Float, nullable=True),
        sa.Column("status", recording_status, nullable=False, server_default="pending"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    session_status = postgresql.ENUM(
        "pending", "aligning", "analyzing", "complete", "failed", name="sessionstatus"
    )

    op.create_table(
        "analysis_sessions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column(
            "reference_recording_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("recordings.id"),
            nullable=False,
        ),
        sa.Column(
            "student_recording_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("recordings.id"),
            nullable=False,
        ),
        sa.Column("status", session_status, nullable=False, server_default="pending"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    analysis_category = postgresql.ENUM(
        "pitch", "rhythm", "tempo", "dynamics", name="analysiscategory"
    )

    op.create_table(
        "analysis_results",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "session_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("analysis_sessions.id"),
            nullable=False,
        ),
        sa.Column("category", analysis_category, nullable=False),
        sa.Column("data", postgresql.JSONB, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "feedback",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "session_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("analysis_sessions.id"),
            nullable=False,
        ),
        sa.Column("category", analysis_category, nullable=False),
        sa.Column("text", sa.Text, nullable=False),
        sa.Column("timestamp_reference", sa.Float, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table("feedback")
    op.drop_table("analysis_results")
    op.drop_table("analysis_sessions")
    op.drop_table("recordings")
    op.drop_table("users")
    sa.Enum(name="analysiscategory").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="sessionstatus").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="recordingstatus").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="recordingsource").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="recordingtype").drop(op.get_bind(), checkfirst=True)
