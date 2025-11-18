from fastapi import APIRouter

from . import inference, models, training

api_router = APIRouter()

api_router.include_router(models.router)

__all__ = ["api_router"]
