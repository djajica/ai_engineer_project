from fastapi import Depends

from app.core.container import AppContainer, get_container


def get_app_container() -> AppContainer:
    return get_container()


def get_model_registry_service(container: AppContainer = Depends(get_app_container)):
    return container.model_registry_service
