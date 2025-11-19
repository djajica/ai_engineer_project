from functools import lru_cache

from app.graphs.query_agent_graph import QueryAgentGraph
from app.repositories.weaviate_repository import WeaviateRepository
from app.services.query_service import QueryService

from .config import Settings, get_settings


class AppContainer:
    """Lightweight container to share singletons (settings, caches, etc.)."""

    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()

        # Initialize Weaviate repository
        self.weaviate_repo = WeaviateRepository(
            url=self.settings.weaviate_url,
            api_key=self.settings.weaviate_api_key,
            collection_name=self.settings.weaviate_collection_name,
            openai_api_key=self.settings.openai_api_key,
            allow_fallback=self.settings.allow_weaviate_fallback,
        )

        # Initialize query agent graph
        if not self.settings.anthropic_api_key:
            raise ValueError("ANTHROPIC_API_KEY is required")

        self.agent_graph = QueryAgentGraph(
            anthropic_api_key=self.settings.anthropic_api_key,
            tavily_api_key=self.settings.tavily_api_key,
            weaviate_repo=self.weaviate_repo,
        )

        # Initialize query service
        self.query_service = QueryService(
            agent_graph=self.agent_graph,
            weaviate_repo=self.weaviate_repo,
        )


@lru_cache(maxsize=1)
def get_container() -> AppContainer:
    return AppContainer()


def provide_settings() -> Settings:
    """Dependency hook for FastAPI routes."""

    return get_container().settings
