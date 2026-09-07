import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.exceptions import NotFoundError
from app.models.analysis import AnalysisSession
from app.schemas.analysis import AnalysisSessionCreate


async def create_session(db: AsyncSession, payload: AnalysisSessionCreate) -> AnalysisSession:
    session_obj = AnalysisSession(
        user_id=payload.user_id,
        reference_recording_id=payload.reference_recording_id,
        student_recording_id=payload.student_recording_id,
    )
    db.add(session_obj)
    await db.commit()

    from worker.tasks.analyze import process_analysis_session

    process_analysis_session.delay(str(session_obj.id))

    return await get_session(db, session_obj.id)


async def get_session(db: AsyncSession, session_id: uuid.UUID) -> AnalysisSession:
    result = await db.execute(
        select(AnalysisSession)
        .where(AnalysisSession.id == session_id)
        .options(
            selectinload(AnalysisSession.results),
            selectinload(AnalysisSession.feedback_items),
        )
        .execution_options(populate_existing=True)
    )
    session_obj = result.scalar_one_or_none()
    if session_obj is None:
        raise NotFoundError("AnalysisSession", str(session_id))
    return session_obj
