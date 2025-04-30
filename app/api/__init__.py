# API package initialization
from fastapi import APIRouter

from app.api.auth import router as auth_router
from app.api.users import router as users_router

api_router = APIRouter(prefix="/api")
api_router.include_router(auth_router)
api_router.include_router(users_router)

# Add more routers here as your application grows
# api_router.include_router(pets_router)
# api_router.include_router(adoptions_router)
# etc.

__all__ = ["api_router"]
