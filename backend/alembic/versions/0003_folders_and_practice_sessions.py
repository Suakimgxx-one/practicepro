"""add folders, practice_sessions, and piece metadata columns

Revision ID: 0003
Revises: 0002
Create Date: 2026-09-08
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0003"
down_revision = "0002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "folders",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("color", sa.String(20), nullable=False, server_default="violet"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.add_column("pieces", sa.Column("composer", sa.String(255), nullable=True))
    op.add_column("pieces", sa.Column("instrument", sa.String(100), nullable=True))
    op.add_column("pieces", sa.Column("folder_id", postgresql.UUID(as_uuid=True), nullable=True))
    op.create_foreign_key("fk_pieces_folder_id", "pieces", "folders", ["folder_id"], ["id"])

    op.create_table(
        "practice_sessions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("piece_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("pieces.id"), nullable=False),
        sa.Column("focus_section", sa.String(255), nullable=True),
        sa.Column("session_goal", sa.String(255), nullable=True),
        sa.Column("target_tempo_bpm", sa.Integer, nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("ended_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("duration_seconds", sa.Integer, nullable=True),
        sa.Column("reflection_notes", sa.Text, nullable=True),
        sa.Column("self_rating", sa.Integer, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table("practice_sessions")
    op.drop_constraint("fk_pieces_folder_id", "pieces", type_="foreignkey")
    op.drop_column("pieces", "folder_id")
    op.drop_column("pieces", "instrument")
    op.drop_column("pieces", "composer")
    op.drop_table("folders")
