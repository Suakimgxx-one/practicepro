from fastapi import APIRouter

from app.api.routes import analysis, recordings, users

api_router = APIRouter()
api_router.include_router(users.router)
api_router.include_router(recordings.router)
api_router.include_router(analysis.router)
