from fastapi import APIRouter, Depends

from app.api.dependencies import get_query_service
from app.schemas.query_schema import QueryRequest, QueryResponse
from app.services.query_service import QueryService

router = APIRouter(prefix="/query", tags=["query"])


@router.post("", response_model=QueryResponse)
async def query(
    payload: QueryRequest,
    service: QueryService = Depends(get_query_service),
) -> QueryResponse:
    """
    Process a query using LangGraph agent with RAG and web search.

    The agent will:
    - Route to Weaviate (internal docs) or Tavily (web search) based on query
    - Retrieve relevant context
    - Generate answer using Claude
    """
    return await service.query(payload)



