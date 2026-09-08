"""add pieces table and recordings.piece_id

Revision ID: 0002
Revises: 0001
Create Date: 2026-09-07
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "pieces",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("title", sa.String(255), nullable=False),
        # Added as nullable + no FK constraint yet, to avoid a circular
        # dependency at table-creation time (pieces.reference_recording_id
        # -> recordings.id, while recordings.piece_id -> pieces.id).
        # The FK constraint itself is added below, after both tables exist.
        sa.Column("reference_recording_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.add_column(
        "recordings",
        sa.Column("piece_id", postgresql.UUID(as_uuid=True), nullable=True),
    )
    op.create_foreign_key(
        "fk_recordings_piece_id", "recordings", "pieces", ["piece_id"], ["id"]
    )
    op.create_foreign_key(
        "fk_pieces_reference_recording_id",
        "pieces",
        "recordings",
        ["reference_recording_id"],
        ["id"],
    )


def downgrade() -> None:
    op.drop_constraint("fk_pieces_reference_recording_id", "pieces", type_="foreignkey")
    op.drop_constraint("fk_recordings_piece_id", "recordings", type_="foreignkey")
    op.drop_column("recordings", "piece_id")
    op.drop_table("pieces")
