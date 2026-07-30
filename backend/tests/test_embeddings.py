"""Unit tests for sentence transformers embedding generator."""

import pytest
from backend.rag.embeddings import EmbeddingGenerator


def test_embedding_generator_singleton():
    """Verify singleton instance behavior of EmbeddingGenerator."""
    gen1 = EmbeddingGenerator()
    gen2 = EmbeddingGenerator()
    assert gen1 is gen2


def test_embed_text_dimensionality():
    """Verify single text embedding produces 384-dimensional vector for all-MiniLM-L6-v2."""
    generator = EmbeddingGenerator()
    vector = generator.embed_text("Test sentence for vector embedding.")

    assert isinstance(vector, list)
    assert len(vector) == 384
    assert isinstance(vector[0], float)


def test_embed_documents_batch():
    """Verify batch embedding generation for multiple text passages."""
    generator = EmbeddingGenerator()
    passages = [
        "First document passage about science.",
        "Second document passage about technology.",
        "Third document passage about history.",
    ]

    vectors = generator.embed_documents(passages)

    assert len(vectors) == 3
    for vec in vectors:
        assert len(vec) == 384
