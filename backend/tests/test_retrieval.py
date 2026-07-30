"""Dedicated test suite for semantic retrieval pipeline, cosine similarity search, and Top-K ranking accuracy."""

import tempfile
import pytest
from backend.rag.chunker import DocumentChunk
from backend.rag.embeddings import EmbeddingGenerator
from backend.rag.vectorstore import ChromaVectorStore


@pytest.fixture
def test_rag_db():
    """Fixture providing populated vector store with known semantic passages."""
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmp_dir:
        store = ChromaVectorStore(chroma_path=tmp_dir)
        embedder = EmbeddingGenerator()

        chunks = [
            DocumentChunk(
                chunk_id="astronomy_01",
                text="The James Webb Space Telescope studies distant galaxies, stars, and exoplanets in infrared light.",
                document_name="space_exploration.pdf",
                page_number=4,
                chunk_index=0,
            ),
            DocumentChunk(
                chunk_id="culinary_01",
                text="Traditional Italian pizza dough requires flour, water, yeast, salt, and olive oil left to ferment.",
                document_name="recipes.pdf",
                page_number=12,
                chunk_index=0,
            ),
            DocumentChunk(
                chunk_id="finance_01",
                text="Inflation rates impact central bank interest rate decisions and global currency exchange values.",
                document_name="economics.txt",
                page_number=1,
                chunk_index=0,
            ),
        ]

        texts = [c.text for c in chunks]
        embeddings = embedder.embed_documents(texts)
        store.add_chunks(chunks, embeddings)

        yield store, embedder


def test_semantic_retrieval_relevance(test_rag_db):
    """Verify that query for space telescope retrieves astronomy chunk as top match."""
    store, embedder = test_rag_db

    query = "How does the James Webb Space Telescope observe galaxies?"
    query_vector = embedder.embed_text(query)

    results = store.similarity_search(query_vector, top_k=2)

    assert len(results) > 0
    top_match = results[0]

    assert top_match.chunk_id == "astronomy_01"
    assert top_match.document_name == "space_exploration.pdf"
    assert top_match.page_number == 4
    assert top_match.score > 0.4


def test_retrieval_top_k_ordering(test_rag_db):
    """Verify that results are sorted in descending order of similarity score."""
    store, embedder = test_rag_db

    query = "What ingredients make pizza dough?"
    query_vector = embedder.embed_text(query)

    results = store.similarity_search(query_vector, top_k=3)

    assert len(results) == 3
    assert results[0].chunk_id == "culinary_01"

    # Check descending score ordering
    for i in range(len(results) - 1):
        assert results[i].score >= results[i + 1].score
