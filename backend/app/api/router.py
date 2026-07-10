from fastapi import APIRouter

from app.api.routes import recordings, users

# Health check is intentionally mounted separately in main.py, unprefixed —
# load balancers / container orchestrators conventionally expect it at a
# fixed, unversioned path (e.g. /health), not under /api/v1.
api_router = APIRouter()
api_router.include_router(users.router)
api_router.include_router(recordings.router)
