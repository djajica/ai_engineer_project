from fastapi import Depends

from app.core.container import AppContainer, get_container


def get_app_container() -> AppContainer:
    return get_container()


def get_query_service(container: AppContainer = Depends(get_app_container)):
    return container.query_service


def get_weaviate_repository(container: AppContainer = Depends(get_app_container)):
    return container.weaviate_repo
