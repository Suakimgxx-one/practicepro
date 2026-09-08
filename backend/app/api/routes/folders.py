import uuid

from fastapi import APIRouter, status
from sqlalchemy import func, select

from app.api.deps import DBSession
from app.models.piece import Piece
from app.schemas.folder import FolderCreate, FolderRead, FolderUpdate
from app.services import folder_service

router = APIRouter(prefix="/folders", tags=["folders"])


@router.post("", response_model=FolderRead, status_code=status.HTTP_201_CREATED)
async def create_folder(payload: FolderCreate, db: DBSession) -> FolderRead:
    return await folder_service.create_folder(db, payload)


@router.get("", response_model=list[FolderRead])
async def list_folders(db: DBSession, user_id: uuid.UUID) -> list[FolderRead]:
    return await folder_service.list_folders_for_user(db, user_id)


@router.patch("/{folder_id}", response_model=FolderRead)
async def update_folder(folder_id: uuid.UUID, payload: FolderUpdate, db: DBSession) -> FolderRead:
    folder = await folder_service.get_folder(db, folder_id)
    updated = await folder_service.update_folder(db, folder, payload)

    # Explicit count query rather than accessing updated.pieces lazily —
    # that relationship isn't eagerly loaded here, and an implicit lazy
    # load on an async session outside an awaited context raises
    # MissingGreenlet (see app/services/analysis_service.py for the
    # same class of bug hit earlier in this project).
    count_result = await db.execute(select(func.count(Piece.id)).where(Piece.folder_id == updated.id))
    piece_count = count_result.scalar_one()

    return FolderRead.model_validate(updated).model_copy(update={"piece_count": piece_count})


@router.delete("/{folder_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_folder(folder_id: uuid.UUID, db: DBSession) -> None:
    folder = await folder_service.get_folder(db, folder_id)
    await folder_service.delete_folder(db, folder)
