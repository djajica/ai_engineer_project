from fastapi import APIRouter, Depends

from app.api.dependencies import get_model_registry_service
from app.schemas import ModelInfo
from app.services.model_registry_service import ModelRegistryService

router = APIRouter(prefix="/api/v1/models", tags=["models"])


@router.get("", response_model=list[ModelInfo])
async def list_models(
    service: ModelRegistryService = Depends(get_model_registry_service),
) -> list[ModelInfo]:
    return await service.list_models()
