from fastapi import APIRouter

from . import ingest, query

api_router = APIRouter()
api_router.include_router(query.router)
api_router.include_router(ingest.router)

__all__ = ["api_router"]
