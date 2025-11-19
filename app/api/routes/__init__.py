from fastapi import APIRouter

from . import ingest_routes, query_routes, weaviate_routes

api_router = APIRouter()
api_router.include_router(query_routes.router)
api_router.include_router(ingest_routes.router)
api_router.include_router(weaviate_routes.router)

__all__ = ["api_router"]
