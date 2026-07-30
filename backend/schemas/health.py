"""Health status response schemas."""

from typing import Any, Dict
from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    """System health check response model."""

    status: str = Field(description="Overall server status string (healthy/degraded/unhealthy).")
    ollama: Dict[str, Any] = Field(description="Local Ollama server connectivity status.")
    vector_store: Dict[str, Any] = Field(description="ChromaDB vector store connection status.")
    embedding_model: str = Field(description="Name of active local embedding model.")
