import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError
from app.models.folder import Folder
from app.models.piece import Piece
from app.schemas.folder import FolderCreate, FolderRead, FolderUpdate


async def create_folder(db: AsyncSession, payload: FolderCreate) -> FolderRead:
    folder = Folder(user_id=payload.user_id, name=payload.name, color=payload.color)
    db.add(folder)
    await db.commit()
    await db.refresh(folder)
    return FolderRead.model_validate(folder).model_copy(update={"piece_count": 0})


async def list_folders_for_user(db: AsyncSession, user_id: uuid.UUID) -> list[FolderRead]:
    # A single grouped query for piece counts, rather than N+1 queries
    # (one COUNT per folder) — matters once a user has more than a
    # handful of folders.
    result = await db.execute(
        select(Folder, func.count(Piece.id))
        .outerjoin(Piece, Piece.folder_id == Folder.id)
        .where(Folder.user_id == user_id)
        .group_by(Folder.id)
        .order_by(Folder.created_at.asc())
    )
    return [
        FolderRead.model_validate(folder).model_copy(update={"piece_count": count})
        for folder, count in result.all()
    ]


async def get_folder(db: AsyncSession, folder_id: uuid.UUID) -> Folder:
    folder = await db.get(Folder, folder_id)
    if folder is None:
        raise NotFoundError("Folder", str(folder_id))
    return folder


async def update_folder(db: AsyncSession, folder: Folder, payload: FolderUpdate) -> Folder:
    if payload.name is not None:
        folder.name = payload.name
    if payload.color is not None:
        folder.color = payload.color
    await db.commit()
    await db.refresh(folder)
    return folder


async def delete_folder(db: AsyncSession, folder: Folder) -> None:
    # Pieces in this folder are NOT deleted — they simply become
    # unfiled (folder_id set to NULL), matching the brief's requirement
    # that pieces can exist outside any folder.
    result = await db.execute(select(Piece).where(Piece.folder_id == folder.id))
    for piece in result.scalars().all():
        piece.folder_id = None
    await db.delete(folder)
    await db.commit()
