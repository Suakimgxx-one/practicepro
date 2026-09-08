import uuid

from fastapi import APIRouter, status

from app.api.deps import DBSession
from app.models.analysis import AnalysisSession
from app.schemas.analysis import (
    AnalysisResultRead,
    AnalysisSessionCreate,
    AnalysisSessionDetail,
)
from app.schemas.feedback import FeedbackRead
from app.services import analysis_service

router = APIRouter(prefix="/analysis-sessions", tags=["analysis"])


def _to_detail(session_obj: AnalysisSession) -> AnalysisSessionDetail:
    return AnalysisSessionDetail(
        id=session_obj.id,
        user_id=session_obj.user_id,
        reference_recording_id=session_obj.reference_recording_id,
        student_recording_id=session_obj.student_recording_id,
        status=session_obj.status,
        created_at=session_obj.created_at,
        results=[AnalysisResultRead.model_validate(r) for r in session_obj.results],
        feedback=[FeedbackRead.model_validate(f) for f in session_obj.feedback_items],
    )


@router.post("", response_model=AnalysisSessionDetail, status_code=status.HTTP_201_CREATED)
async def create_analysis_session(
    payload: AnalysisSessionCreate, db: DBSession
) -> AnalysisSessionDetail:
    session_obj = await analysis_service.create_session(db, payload)
    return _to_detail(session_obj)


@router.get("/{session_id}", response_model=AnalysisSessionDetail)
async def get_analysis_session(session_id: uuid.UUID, db: DBSession) -> AnalysisSessionDetail:
    session_obj = await analysis_service.get_session(db, session_id)
    return _to_detail(session_obj)
