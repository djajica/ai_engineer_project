from pydantic import BaseModel, Field


class QueryRequest(BaseModel):
    """Request schema for query endpoint."""

    query: str = Field(..., min_length=1, description="User query string")


class QueryResponse(BaseModel):
    """Response schema for query endpoint."""

    answer: str = Field(..., description="Generated answer from LLM")
    sources: list[str] = Field(
        default_factory=list, description="Source URLs or document IDs"
    )

