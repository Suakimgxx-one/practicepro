import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.exceptions import NotFoundError
from app.models.analysis import AnalysisCategory, AnalysisSession, SessionStatus
from app.models.piece import Piece
from app.models.practice_session import PracticeSession
from app.schemas.piece import PieceCreate, PieceDetail, PieceProgressPoint, PieceUpdate


async def create_piece(db: AsyncSession, payload: PieceCreate) -> Piece:
    piece = Piece(
        user_id=payload.user_id,
        title=payload.title,
        composer=payload.composer,
        instrument=payload.instrument,
        folder_id=payload.folder_id,
    )
    db.add(piece)
    await db.commit()
    await db.refresh(piece)
    return piece


async def list_pieces_for_user(db: AsyncSession, user_id: uuid.UUID) -> list[Piece]:
    result = await db.execute(
        select(Piece).where(Piece.user_id == user_id).order_by(Piece.created_at.desc())
    )
    return list(result.scalars().all())


async def get_piece(db: AsyncSession, piece_id: uuid.UUID) -> Piece:
    piece = await db.get(Piece, piece_id)
    if piece is None:
        raise NotFoundError("Piece", str(piece_id))
    return piece


async def update_piece(db: AsyncSession, piece: Piece, payload: PieceUpdate) -> Piece:
    if payload.title is not None:
        piece.title = payload.title
    if payload.composer is not None:
        piece.composer = payload.composer
    if payload.instrument is not None:
        piece.instrument = payload.instrument
    if "folder_id" in payload.model_fields_set:
        piece.folder_id = payload.folder_id
    await db.commit()
    await db.refresh(piece)
    return piece


async def get_piece_detail(db: AsyncSession, piece_id: uuid.UUID) -> PieceDetail:
    result = await db.execute(
        select(Piece)
        .where(Piece.id == piece_id)
        .options(selectinload(Piece.reference_recording), selectinload(Piece.attempts))
        .execution_options(populate_existing=True)
    )
    piece = result.scalar_one_or_none()
    if piece is None:
        raise NotFoundError("Piece", str(piece_id))

    progress = await _build_progress(db, [attempt.id for attempt in piece.attempts])

    sessions_result = await db.execute(
        select(PracticeSession)
        .where(PracticeSession.piece_id == piece_id)
        .order_by(PracticeSession.started_at.desc())
    )
    practice_sessions = list(sessions_result.scalars().all())
    total_practice_seconds = sum(s.duration_seconds or 0 for s in practice_sessions)

    return PieceDetail(
        id=piece.id,
        user_id=piece.user_id,
        title=piece.title,
        composer=piece.composer,
        instrument=piece.instrument,
        folder_id=piece.folder_id,
        reference_recording_id=piece.reference_recording_id,
        created_at=piece.created_at,
        reference_recording=piece.reference_recording,
        attempts=list(piece.attempts),
        progress=progress,
        practice_sessions=practice_sessions,
        total_practice_seconds=total_practice_seconds,
    )


async def _build_progress(
    db: AsyncSession, attempt_recording_ids: list[uuid.UUID]
) -> list[PieceProgressPoint]:
    if not attempt_recording_ids:
        return []

    result = await db.execute(
        select(AnalysisSession)
        .where(
            AnalysisSession.student_recording_id.in_(attempt_recording_ids),
            AnalysisSession.status == SessionStatus.COMPLETE,
        )
        .options(selectinload(AnalysisSession.results))
        .order_by(AnalysisSession.created_at.asc())
    )
    sessions = result.scalars().all()

    points: list[PieceProgressPoint] = []
    for session_obj in sessions:
        stats: dict[str, float] = {}
        for result_row in session_obj.results:
            if result_row.category == AnalysisCategory.PITCH:
                value = result_row.data.get("mean_absolute_cents_deviation")
                if value is not None:
                    stats["mean_absolute_cents_deviation"] = value
            elif result_row.category == AnalysisCategory.RHYTHM:
                value = result_row.data.get("mean_absolute_timing_offset_seconds")
                if value is not None:
                    stats["mean_absolute_timing_offset_seconds"] = value
            elif result_row.category == AnalysisCategory.TEMPO:
                value = result_row.data.get("mean_tempo_ratio")
                if value is not None:
                    stats["mean_tempo_ratio"] = value
            elif result_row.category == AnalysisCategory.DYNAMICS:
                value = result_row.data.get("mean_absolute_loudness_difference_db")
                if value is not None:
                    stats["mean_absolute_loudness_difference_db"] = value

        points.append(
            PieceProgressPoint(
                session_id=session_obj.id,
                student_recording_id=session_obj.student_recording_id,
                created_at=session_obj.created_at,
                **stats,
            )
        )

    return points
