from fastapi import APIRouter

from app.api.routes import analysis, folders, pieces, practice_sessions, recordings, users

api_router = APIRouter()
api_router.include_router(users.router)
api_router.include_router(folders.router)
api_router.include_router(pieces.router)
api_router.include_router(recordings.router)
api_router.include_router(analysis.router)
api_router.include_router(practice_sessions.router)
