"""Document ingestion API router (POST /ingest)."""

from pathlib import Path
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status

from backend.api.dependencies import get_rag_pipeline_dep, get_settings_dep
from backend.config.settings import Settings
from backend.logging.logger import get_logger
from backend.rag.pipeline import RAGPipeline
from backend.schemas.document import IngestResponse

logger = get_logger(__name__)
router = APIRouter(tags=["Document Ingestion"])

ALLOWED_EXTENSIONS = {".pdf", ".docx", ".txt"}


@router.post(
    "/ingest",
    response_model=IngestResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Ingest Document File (PDF, DOCX, TXT)",
    description="Uploads a PDF, DOCX, or TXT document, parses its text, chunks it, generates embeddings, and persists to ChromaDB.",
)
async def ingest_document(
    file: UploadFile = File(...),
    pipeline: RAGPipeline = Depends(get_rag_pipeline_dep),
    settings: Settings = Depends(get_settings_dep),
) -> IngestResponse:
    """Handle multipart document upload and execute full ingestion pipeline."""
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Filename cannot be empty.",
        )

    file_path = Path(file.filename)
    file_ext = file_path.suffix.lower()

    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file format '{file_ext}'. Allowed formats: {list(ALLOWED_EXTENSIONS)}",
        )

    storage_dir = settings.get_absolute_storage_dir()
    save_path = storage_dir / file_path.name

    try:
        logger.info(f"Saving uploaded file '{file.filename}' to storage...")
        contents = await file.read()
        with open(save_path, "wb") as f:
            f.write(contents)

        # Run ingestion pipeline
        result = pipeline.ingest_document(save_path)

        return IngestResponse(
            message=f"Document '{file.filename}' successfully ingested and indexed.",
            document_name=result["document_name"],
            total_pages=result["total_pages"],
            total_chunks=result["total_chunks"],
            file_type=file_ext.lstrip("."),
        )

    except ValueError as err:
        logger.error(f"Validation error during ingestion of '{file.filename}': {str(err)}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(err),
        ) from err
    except Exception as err:
        logger.error(f"Unhandled error during ingestion of '{file.filename}': {str(err)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to ingest document: {str(err)}",
        ) from err
