from functools import lru_cache


from app.repositories.model_repository import ModelRepository

from app.utils.model_cache import ModelCache

from .config import Settings, get_settings


class AppContainer:
    """Lightweight container to share singletons (settings, caches, etc.)."""

    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()

        self.model_registry_service = ModelRegistryService(self.registry_repo)


@lru_cache(maxsize=1)
def get_container() -> AppContainer:
    return AppContainer()


def provide_settings() -> Settings:
    """Dependency hook for FastAPI routes."""

    return get_container().settings
