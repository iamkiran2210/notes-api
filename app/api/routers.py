from fastapi import APIRouter
from app.api.endpoints import health, auth, notes

router = APIRouter()

router.include_router(auth.router, prefix="/auth", tags=["auth"])
router.include_router(health.router, prefix="/health", tags=["health"])
router.include_router(notes.router, prefix="/notes", tags=["notes"])
