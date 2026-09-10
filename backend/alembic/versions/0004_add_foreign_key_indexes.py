"""add indexes to all foreign key columns

Revision ID: 0004
Revises: 0003
Create Date: 2026-09-10

Postgres does NOT automatically create an index on a foreign key
column — it only indexes the primary key being referenced. Every one
of these columns is used in a WHERE clause somewhere in the app
(e.g. "get all recordings for this piece", "get all sessions for
this user"), so without an explicit index, those queries do a full
table scan once the tables have real volume.
"""
from alembic import op

revision = "0004"
down_revision = "0003"
branch_labels = None
depends_on = None

INDEXES = [
    ("ix_recordings_user_id", "recordings", "user_id"),
    ("ix_recordings_piece_id", "recordings", "piece_id"),
    ("ix_analysis_sessions_user_id", "analysis_sessions", "user_id"),
    ("ix_analysis_sessions_reference_recording_id", "analysis_sessions", "reference_recording_id"),
    ("ix_analysis_sessions_student_recording_id", "analysis_sessions", "student_recording_id"),
    ("ix_analysis_results_session_id", "analysis_results", "session_id"),
    ("ix_feedback_session_id", "feedback", "session_id"),
    ("ix_pieces_user_id", "pieces", "user_id"),
    ("ix_pieces_folder_id", "pieces", "folder_id"),
    ("ix_pieces_reference_recording_id", "pieces", "reference_recording_id"),
    ("ix_folders_user_id", "folders", "user_id"),
    ("ix_practice_sessions_user_id", "practice_sessions", "user_id"),
    ("ix_practice_sessions_piece_id", "practice_sessions", "piece_id"),
]


def upgrade() -> None:
    for index_name, table_name, column_name in INDEXES:
        op.create_index(index_name, table_name, [column_name])


def downgrade() -> None:
    for index_name, table_name, _column_name in INDEXES:
        op.drop_index(index_name, table_name=table_name)
