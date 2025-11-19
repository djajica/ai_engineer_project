from app.graphs.query_agent_graph import QueryAgentGraph
from app.repositories.weaviate_repository import WeaviateRepository
from app.schemas.query_schema import QueryRequest, QueryResponse


class QueryService:
    """Service for processing queries using LangGraph agent."""

    def __init__(
        self,
        agent_graph: QueryAgentGraph,
        weaviate_repo: WeaviateRepository,
    ) -> None:
        """
        Initialize query service.

        Args:
            agent_graph: QueryAgentGraph instance
            weaviate_repo: WeaviateRepository instance
        """
        self.agent_graph = agent_graph
        self.weaviate_repo = weaviate_repo

    async def query(self, payload: QueryRequest) -> QueryResponse:
        """
        Process a query using the LangGraph agent.

        Args:
            payload: QueryRequest with user query

        Returns:
            QueryResponse with answer and sources
        """
        result = await self.agent_graph.run(payload.query)

        answer = result.get("response", "I couldn't generate a response.")
        sources = result.get("sources", [])

        return QueryResponse(answer=answer, sources=sources)


