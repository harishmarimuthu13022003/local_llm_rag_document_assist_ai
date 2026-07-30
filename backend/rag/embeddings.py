"""Embedding generator using Sentence Transformers.

Uses `sentence-transformers/all-MiniLM-L6-v2` model to generate 384-dimensional dense vectors locally.
"""

import time
from typing import List, Union

from sentence_transformers import SentenceTransformer

from backend.config.settings import get_settings
from backend.logging.logger import get_logger

logger = get_logger(__name__)


class EmbeddingGenerator:
    """SentenceTransformer embedding generator singleton manager."""

    _instance: Union["EmbeddingGenerator", None] = None
    _model: Union[SentenceTransformer, None] = None

    def __new__(cls) -> "EmbeddingGenerator":
        """Singleton instance retriever."""
        if cls._instance is None:
            cls._instance = super(EmbeddingGenerator, cls).__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        """Initialize SentenceTransformer model if not already loaded."""
        if self._model is None:
            settings = get_settings()
            model_name = settings.embedding_model
            logger.info(f"Loading local embedding model: '{model_name}'...")
            start_time = time.perf_counter()
            self._model = SentenceTransformer(model_name)
            elapsed_ms = (time.perf_counter() - start_time) * 1000
            logger.info(f"Loaded embedding model in {elapsed_ms:.2f}ms.")

    @property
    def model(self) -> SentenceTransformer:
        """Get underlying SentenceTransformer model instance.

        Returns:
            SentenceTransformer: Model instance.
        """
        if self._model is None:
            raise RuntimeError("Embedding model is not initialized.")
        return self._model

    def embed_text(self, text: str) -> List[float]:
        """Generate vector embedding for a single text string.

        Args:
            text: Input string.

        Returns:
            List[float]: 384-dimensional floating point embedding vector.
        """
        start_time = time.perf_counter()
        vector = self.model.encode(text, convert_to_numpy=True).tolist()
        elapsed_ms = (time.perf_counter() - start_time) * 1000
        logger.debug(
            f"Generated single embedding in {elapsed_ms:.2f}ms.",
            extra={"embedding_latency_ms": elapsed_ms},
        )
        return vector

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Generate batch vector embeddings for multiple text strings.

        Args:
            texts: List of input strings.

        Returns:
            List[List[float]]: List of 384-dimensional embedding vectors.
        """
        if not texts:
            return []

        start_time = time.perf_counter()
        vectors = self.model.encode(texts, convert_to_numpy=True, batch_size=32).tolist()
        elapsed_ms = (time.perf_counter() - start_time) * 1000
        logger.info(
            f"Generated batch embeddings for {len(texts)} chunks in {elapsed_ms:.2f}ms.",
            extra={"embedding_latency_ms": elapsed_ms, "chunk_count": len(texts)},
        )
        return vectors
