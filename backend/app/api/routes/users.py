import uuid

from fastapi import APIRouter, status

from app.api.deps import DBSession
from app.schemas.user import UserCreate, UserRead
from app.services import user_service

router = APIRouter(prefix="/users", tags=["users"])


@router.post("", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def create_user(payload: UserCreate, db: DBSession) -> UserRead:
    existing = await user_service.get_user_by_email(db, payload.email)
    if existing is not None:
        return existing
    return await user_service.create_user(db, payload)


@router.get("/{user_id}", response_model=UserRead)
async def get_user(user_id: uuid.UUID, db: DBSession) -> UserRead:
    return await user_service.get_user(db, user_id)
