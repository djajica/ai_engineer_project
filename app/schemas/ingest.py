from pydantic import BaseModel, Field


class IngestResponse(BaseModel):
    """Response schema for document ingestion endpoint."""

    status: str = Field(..., description="Ingestion status")
    count: int = Field(..., ge=0, description="Number of documents ingested")



