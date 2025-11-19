from pathlib import Path
from tempfile import NamedTemporaryFile

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status

from app.api.dependencies import get_weaviate_repository
from app.repositories.weaviate_repository import WeaviateRepository
from app.schemas.ingest import IngestResponse
from app.utils.pdf_parser import parse_pdf

router = APIRouter(prefix="/ingest", tags=["ingest"])


@router.post("/pdf", response_model=IngestResponse)
async def ingest_pdf(
    file: UploadFile = File(...),
    repo: WeaviateRepository = Depends(get_weaviate_repository),
) -> IngestResponse:
    """
    Upload and ingest PDF file into Weaviate.

    PDF will be parsed and split into chunks for indexing.
    Works for PDFs of any size.
    """
    # Validate file type
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF files are supported",
        )

    # Save uploaded file temporarily
    with NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
        content = await file.read()
        tmp_file.write(content)
        tmp_path = tmp_file.name

    try:
        # Parse PDF into chunks
        chunks = parse_pdf(tmp_path)

        if not chunks:
            return IngestResponse(
                status="error",
                count=0,
            )

        # Add to Weaviate
        documents = [
            {"text": chunk["text"], "metadata": chunk["metadata"]}
            for chunk in chunks
        ]
        repo.add_documents(documents)

        return IngestResponse(status="success", count=len(documents))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing PDF: {str(e)}",
        )
    finally:
        # Cleanup temp file
        Path(tmp_path).unlink(missing_ok=True)