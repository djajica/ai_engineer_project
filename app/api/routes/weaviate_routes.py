from fastapi import APIRouter, Depends, Query

from app.api.dependencies import get_weaviate_repository
from app.repositories.weaviate_repository import WeaviateRepository

router = APIRouter(prefix="/weaviate", tags=["weaviate"])


@router.get("/status")
def get_weaviate_status(
    repo: WeaviateRepository = Depends(get_weaviate_repository),
) -> dict[str, object]:
    """Return current Weaviate status and collection statistics."""

    return repo.get_status()


@router.get("/objects")
def list_weaviate_objects(
    limit: int = Query(
        default=20,
        ge=1,
        le=200,
        description="Maximum number of objects to return",
    ),
    repo: WeaviateRepository = Depends(get_weaviate_repository),
) -> dict[str, object]:
    """Return recent objects stored in Weaviate for quick inspection."""

    objects = repo.list_objects(limit=limit)
    return {"count": len(objects), "items": objects}

