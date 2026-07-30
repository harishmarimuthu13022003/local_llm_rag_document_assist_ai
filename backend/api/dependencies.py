"""FastAPI dependency injection factories for services and repositories."""

from functools import lru_cache
from backend.config.settings import Settings, get_settings
from backend.rag.pipeline import RAGPipeline
from backend.rag.vectorstore import ChromaVectorStore

_rag_pipeline_instance: RAGPipeline | None = None
_vector_store_instance: ChromaVectorStore | None = None


def get_settings_dep() -> Settings:
    """Dependency provider for Settings."""
    return get_settings()


def get_vector_store_dep() -> ChromaVectorStore:
    """Dependency provider for singleton ChromaVectorStore."""
    global _vector_store_instance
    if _vector_store_instance is None:
        _vector_store_instance = ChromaVectorStore()
    return _vector_store_instance


def get_rag_pipeline_dep() -> RAGPipeline:
    """Dependency provider for singleton RAGPipeline orchestrator."""
    global _rag_pipeline_instance
    if _rag_pipeline_instance is None:
        vector_store = get_vector_store_dep()
        _rag_pipeline_instance = RAGPipeline(vector_store=vector_store)
    return _rag_pipeline_instance
