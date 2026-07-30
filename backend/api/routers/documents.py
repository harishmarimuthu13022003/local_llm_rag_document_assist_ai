"""Document management API router (GET /documents, GET /sources/{id}, DELETE /documents/{id})."""

from fastapi import APIRouter, Depends, HTTPException, status

from backend.api.dependencies import get_vector_store_dep, get_settings_dep
from backend.config.settings import Settings
from backend.logging.logger import get_logger
from backend.rag.vectorstore import ChromaVectorStore
from backend.schemas.document import (
    ChunkDetail,
    DocumentChunksResponse,
    DocumentListResponse,
    DocumentSummary,
)

logger = get_logger(__name__)
router = APIRouter(tags=["Document Management"])


@router.get(
    "/documents",
    response_model=DocumentListResponse,
    summary="List All Ingested Documents",
    description="Returns a summary list of all document files indexed in the vector store.",
)
async def list_documents(
    vector_store: ChromaVectorStore = Depends(get_vector_store_dep),
) -> DocumentListResponse:
    """Fetch list of indexed documents with chunk count and page metadata."""
    doc_summaries = vector_store.list_documents()

    docs = [
        DocumentSummary(
            document_name=d["document_name"],
            chunk_count=d["chunk_count"],
            max_page=d["max_page"],
            file_type=d["file_type"],
        )
        for d in doc_summaries
    ]

    return DocumentListResponse(documents=docs, total_count=len(docs))


@router.get(
    "/sources/{id}",
    response_model=DocumentChunksResponse,
    summary="Get Document Chunks & Source Details",
    description="Retrieves all chunk text passages and metadata associated with a specific document identifier.",
)
async def get_document_sources(
    id: str,
    vector_store: ChromaVectorStore = Depends(get_vector_store_dep),
) -> DocumentChunksResponse:
    """Fetch chunk details for specified document name or ID."""
    doc_name = id.strip()
    chunk_records = vector_store.get_document_chunks(doc_name)

    if not chunk_records:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No document chunks found matching identifier '{doc_name}'.",
        )

    chunks = [
        ChunkDetail(
            chunk_id=c["chunk_id"],
            text=c["text"],
            document_name=c["document_name"],
            page_number=c["page_number"],
            chunk_index=c["chunk_index"],
            metadata=c["metadata"],
        )
        for c in chunk_records
    ]

    return DocumentChunksResponse(
        document_name=doc_name,
        chunks=chunks,
        total_chunks=len(chunks),
    )


@router.delete(
    "/documents/{id}",
    status_code=status.HTTP_200_OK,
    summary="Delete Document from Vector Store",
    description="Removes all chunks of the specified document from ChromaDB persistent storage.",
)
async def delete_document(
    id: str,
    vector_store: ChromaVectorStore = Depends(get_vector_store_dep),
    settings: Settings = Depends(get_settings_dep),
) -> dict:
    """Delete document chunks from vector store and remove local file if present."""
    doc_name = id.strip()
    deleted_count = vector_store.delete_document(doc_name)

    if deleted_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document '{doc_name}' not found in vector storage.",
        )

    # Optionally remove physical file from storage_dir if present
    file_path = settings.get_absolute_storage_dir() / doc_name
    if file_path.exists():
        try:
            file_path.unlink()
        except Exception as err:
            logger.warning(f"Could not remove file '{file_path}': {str(err)}")

    return {
        "message": f"Successfully deleted document '{doc_name}' and {deleted_count} associated chunks.",
        "deleted_chunks": deleted_count,
    }
