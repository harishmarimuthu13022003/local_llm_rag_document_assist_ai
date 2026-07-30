"""Health check API router (GET /health)."""

from fastapi import APIRouter, Depends
from backend.api.dependencies import get_rag_pipeline_dep, get_settings_dep
from backend.config.settings import Settings
from backend.rag.pipeline import RAGPipeline
from backend.schemas.health import HealthResponse

router = APIRouter(tags=["Health"])


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="System Health & Connectivity Status",
    description="Returns status of backend, local Ollama LLM server connection, and ChromaDB vector store.",
)
async def health_check(
    pipeline: RAGPipeline = Depends(get_rag_pipeline_dep),
    settings: Settings = Depends(get_settings_dep),
) -> HealthResponse:
    """Execute health status check on local Ollama server and Chroma vector database."""
    ollama_status = await pipeline.llm_client.check_health()

    vector_status = {
        "connected": True,
        "chroma_path": str(settings.get_absolute_chroma_path()),
        "collection": pipeline.vector_store.COLLECTION_NAME,
    }

    overall_healthy = ollama_status.get("server_connected", False)

    return HealthResponse(
        status="healthy" if overall_healthy else "degraded",
        ollama=ollama_status,
        vector_store=vector_status,
        embedding_model=settings.embedding_model,
    )
