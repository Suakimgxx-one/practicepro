import uuid
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError
from app.models.practice_session import PracticeSession
from app.schemas.practice_session import PracticeSessionFinish, PracticeSessionStart


async def start_session(db: AsyncSession, payload: PracticeSessionStart) -> PracticeSession:
    session_obj = PracticeSession(
        user_id=payload.user_id,
        piece_id=payload.piece_id,
        focus_section=payload.focus_section,
        session_goal=payload.session_goal,
        target_tempo_bpm=payload.target_tempo_bpm,
    )
    db.add(session_obj)
    await db.commit()
    await db.refresh(session_obj)
    return session_obj


async def get_session(db: AsyncSession, session_id: uuid.UUID) -> PracticeSession:
    session_obj = await db.get(PracticeSession, session_id)
    if session_obj is None:
        raise NotFoundError("PracticeSession", str(session_id))
    return session_obj


async def finish_session(
    db: AsyncSession, session_obj: PracticeSession, payload: PracticeSessionFinish
) -> PracticeSession:
    ended_at = datetime.now(timezone.utc)
    started_at = session_obj.started_at
    if started_at.tzinfo is None:
        started_at = started_at.replace(tzinfo=timezone.utc)

    session_obj.ended_at = ended_at
    session_obj.duration_seconds = max(0, int((ended_at - started_at).total_seconds()))
    session_obj.reflection_notes = payload.reflection_notes
    session_obj.self_rating = payload.self_rating

    await db.commit()
    await db.refresh(session_obj)
    return session_obj


async def list_sessions_for_piece(db: AsyncSession, piece_id: uuid.UUID) -> list[PracticeSession]:
    result = await db.execute(
        select(PracticeSession)
        .where(PracticeSession.piece_id == piece_id)
        .order_by(PracticeSession.started_at.desc())
    )
    return list(result.scalars().all())


async def list_sessions_for_user(db: AsyncSession, user_id: uuid.UUID) -> list[PracticeSession]:
    result = await db.execute(
        select(PracticeSession)
        .where(PracticeSession.user_id == user_id)
        .order_by(PracticeSession.started_at.desc())
    )
    return list(result.scalars().all())
