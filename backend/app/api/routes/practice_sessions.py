import uuid

from fastapi import APIRouter, status

from app.api.deps import DBSession
from app.schemas.practice_session import (
    PracticeSessionFinish,
    PracticeSessionRead,
    PracticeSessionStart,
)
from app.services import practice_session_service

router = APIRouter(prefix="/practice-sessions", tags=["practice-sessions"])


@router.post("", response_model=PracticeSessionRead, status_code=status.HTTP_201_CREATED)
async def start_practice_session(
    payload: PracticeSessionStart, db: DBSession
) -> PracticeSessionRead:
    """Starts a real timer session — started_at is set server-side at
    creation. The frontend runs its own visible clock, but elapsed time
    is always ultimately computed from this timestamp at finish, not
    trusted from the client."""
    return await practice_session_service.start_session(db, payload)


@router.get("/{session_id}", response_model=PracticeSessionRead)
async def get_practice_session(session_id: uuid.UUID, db: DBSession) -> PracticeSessionRead:
    return await practice_session_service.get_session(db, session_id)


@router.patch("/{session_id}/finish", response_model=PracticeSessionRead)
async def finish_practice_session(
    session_id: uuid.UUID, payload: PracticeSessionFinish, db: DBSession
) -> PracticeSessionRead:
    session_obj = await practice_session_service.get_session(db, session_id)
    return await practice_session_service.finish_session(db, session_obj, payload)


@router.get("", response_model=list[PracticeSessionRead])
async def list_practice_sessions(db: DBSession, piece_id: uuid.UUID) -> list[PracticeSessionRead]:
    return await practice_session_service.list_sessions_for_piece(db, piece_id)
