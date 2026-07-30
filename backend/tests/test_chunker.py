"""Unit tests for text chunker and document page splitter."""

import pytest
from backend.rag.chunker import TextChunker
from backend.rag.loaders import DocumentPage


def test_chunker_initialization_validation():
    """Verify that chunk_overlap >= chunk_size raises ValueError."""
    with pytest.raises(ValueError):
        TextChunker(chunk_size=100, chunk_overlap=100)

    with pytest.raises(ValueError):
        TextChunker(chunk_size=100, chunk_overlap=150)


def test_chunk_document_pages():
    """Verify recursive splitting of document page text into bounded chunks."""
    chunker = TextChunker(chunk_size=100, chunk_overlap=20)

    sample_page = DocumentPage(
        page_number=1,
        text="Sentence one is clear. Sentence two is very informative. Sentence three adds more details. Sentence four concludes.",
        document_name="sample_test.pdf",
        total_pages=1,
        extra_metadata={"file_type": "pdf"},
    )

    chunks = chunker.chunk_document_pages([sample_page])

    assert len(chunks) > 0
    for chunk in chunks:
        assert len(chunk.text) <= 150  # Allows slight buffer for sentence completion
        assert chunk.document_name == "sample_test.pdf"
        assert chunk.page_number == 1
        assert "chunk_id" in chunk.metadata
        assert chunk.metadata["file_type"] == "pdf"


def test_chunk_ids_uniqueness():
    """Verify that generated chunk IDs are unique across multiple chunks."""
    chunker = TextChunker(chunk_size=50, chunk_overlap=10)
    pages = [
        DocumentPage(
            page_number=1,
            text="Paragraph one with lots of descriptive text for testing chunking ID uniqueness.",
            document_name="doc_a.txt",
            total_pages=1,
            extra_metadata={},
        )
    ]
    chunks = chunker.chunk_document_pages(pages)
    chunk_ids = [c.chunk_id for c in chunks]

    assert len(chunk_ids) == len(set(chunk_ids))
