"""Document ingestion and retrieval response schemas."""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class IngestResponse(BaseModel):
    """Document upload and ingestion response schema."""

    message: str = Field(description="Human readable success message.")
    document_name: str = Field(description="Ingested document filename.")
    total_pages: int = Field(description="Total parsed page count.")
    total_chunks: int = Field(description="Total generated vector chunks count.")
    file_type: str = Field(description="Document format extension (pdf/docx/txt).")


class DocumentSummary(BaseModel):
    """Summary record of an ingested document."""

    document_name: str = Field(description="Document filename.")
    chunk_count: int = Field(description="Number of vector passages created.")
    max_page: int = Field(description="Total pages count.")
    file_type: str = Field(description="File extension type.")


class DocumentListResponse(BaseModel):
    """List response schema for GET /documents endpoint."""

    documents: List[DocumentSummary] = Field(description="List of ingested documents.")
    total_count: int = Field(description="Total unique documents count.")


class ChunkDetail(BaseModel):
    """Chunk detail record for GET /sources/{id} endpoint."""

    chunk_id: str = Field(description="Unique vector chunk ID.")
    text: str = Field(description="Passage text content.")
    document_name: str = Field(description="Source document name.")
    page_number: int = Field(description="Source page number.")
    chunk_index: int = Field(description="Chunk sequence index.")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Metadata key-value pairs.")


class DocumentChunksResponse(BaseModel):
    """Response schema for GET /sources/{id} endpoint."""

    document_name: str = Field(description="Target document name.")
    chunks: List[ChunkDetail] = Field(description="List of document chunk passages.")
    total_chunks: int = Field(description="Total chunk count for document.")
