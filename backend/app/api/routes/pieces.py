import uuid

from fastapi import APIRouter, status

from app.api.deps import DBSession
from app.schemas.piece import PieceCreate, PieceDetail, PieceRead, PieceUpdate
from app.services import piece_service

router = APIRouter(prefix="/pieces", tags=["pieces"])


@router.post("", response_model=PieceRead, status_code=status.HTTP_201_CREATED)
async def create_piece(payload: PieceCreate, db: DBSession) -> PieceRead:
    return await piece_service.create_piece(db, payload)


@router.get("", response_model=list[PieceRead])
async def list_pieces(db: DBSession, user_id: uuid.UUID) -> list[PieceRead]:
    return await piece_service.list_pieces_for_user(db, user_id)


@router.get("/{piece_id}", response_model=PieceDetail)
async def get_piece(piece_id: uuid.UUID, db: DBSession) -> PieceDetail:
    return await piece_service.get_piece_detail(db, piece_id)


@router.patch("/{piece_id}", response_model=PieceRead)
async def update_piece(piece_id: uuid.UUID, payload: PieceUpdate, db: DBSession) -> PieceRead:
    """Used for renaming, editing metadata, or moving a piece between
    folders (including back to unfiled, via folder_id: null)."""
    piece = await piece_service.get_piece(db, piece_id)
    return await piece_service.update_piece(db, piece, payload)
