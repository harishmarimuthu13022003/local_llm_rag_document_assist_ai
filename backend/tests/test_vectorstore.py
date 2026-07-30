"""Unit tests for persistent ChromaDB vector store operations."""

import tempfile
import pytest
from backend.rag.chunker import DocumentChunk
from backend.rag.vectorstore import ChromaVectorStore


@pytest.fixture
def temp_vector_store():
    """Fixture initializing temporary ChromaDB storage directory for testing."""
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmp_dir:
        store = ChromaVectorStore(chroma_path=tmp_dir)
        yield store


def test_vectorstore_crud(temp_vector_store):
    """Test adding chunks, listing documents, and deleting document records."""
    store = temp_vector_store

    chunk1 = DocumentChunk(
        chunk_id="chunk_001",
        text="Python is a high level programming language.",
        document_name="python_guide.pdf",
        page_number=1,
        chunk_index=0,
        metadata={"file_type": "pdf", "total_pages": 5},
    )

    chunk2 = DocumentChunk(
        chunk_id="chunk_002",
        text="FastAPI is a modern web framework for Python.",
        document_name="python_guide.pdf",
        page_number=2,
        chunk_index=1,
        metadata={"file_type": "pdf", "total_pages": 5},
    )

    dummy_embeddings = [[0.1] * 384, [0.2] * 384]

    # Store chunks
    store.add_chunks([chunk1, chunk2], dummy_embeddings)

    # List documents
    docs = store.list_documents()
    assert len(docs) == 1
    assert docs[0]["document_name"] == "python_guide.pdf"
    assert docs[0]["chunk_count"] == 2

    # Get document chunks
    retrieved_chunks = store.get_document_chunks("python_guide.pdf")
    assert len(retrieved_chunks) == 2
    assert retrieved_chunks[0]["chunk_id"] == "chunk_001"

    # Delete document
    deleted_count = store.delete_document("python_guide.pdf")
    assert deleted_count == 2
    assert len(store.list_documents()) == 0
