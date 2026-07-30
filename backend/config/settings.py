"""System configuration settings management using Pydantic BaseSettings.

Loads and validates configuration from environment variables and `.env` files.
"""

from functools import lru_cache
from pathlib import Path
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application setting model specifying configuration defaults and validation rules."""

    # Local LLM & Ollama Configurations
    ollama_host: str = Field(
        default="http://localhost:11434",
        description="Local Ollama server HTTP base URL.",
    )
    ollama_model: str = Field(
        default="llama3.2:3b",
        description="Name of the Ollama LLM model to execute for answer generation.",
    )

    # RAG & Embedding Pipeline Configurations
    embedding_model: str = Field(
        default="sentence-transformers/all-MiniLM-L6-v2",
        description="HuggingFace model name or path for local vector embeddings.",
    )
    top_k: int = Field(
        default=4,
        ge=1,
        le=20,
        description="Number of most relevant context chunks to retrieve.",
    )
    chunk_size: int = Field(
        default=1000,
        ge=100,
        le=4000,
        description="Maximum character length of each ingested document chunk.",
    )
    chunk_overlap: int = Field(
        default=150,
        ge=0,
        le=1000,
        description="Character overlap count between consecutive document chunks.",
    )
    max_context: int = Field(
        default=4500,
        ge=500,
        le=32000,
        description="Maximum combined character length of retrieved prompt context.",
    )

    # Storage & Log Paths
    chroma_path: str = Field(
        default="storage/chroma",
        description="Path to local ChromaDB persistent vector database directory.",
    )
    storage_dir: str = Field(
        default="storage/uploads",
        description="Path to store uploaded raw document files.",
    )
    log_dir: str = Field(
        default="logs",
        description="Directory path for writing application log files.",
    )

    # Backend Server Configurations
    host: str = Field(default="0.0.0.0", description="API server host address.")
    port: int = Field(default=8000, description="API server listening port.")
    log_level: str = Field(default="INFO", description="Logging verbosity level.")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    def get_absolute_chroma_path(self, base_dir: Optional[Path] = None) -> Path:
        """Resolve and ensure absolute path for ChromaDB storage directory.

        Args:
            base_dir: Optional base directory to resolve relative paths against.

        Returns:
            Path: Absolute resolved path object.
        """
        path = Path(self.chroma_path)
        if not path.is_absolute():
            root = base_dir or Path.cwd()
            path = (root / path).resolve()
        path.mkdir(parents=True, exist_ok=True)
        return path

    def get_absolute_log_dir(self, base_dir: Optional[Path] = None) -> Path:
        """Resolve and ensure absolute path for logs directory.

        Args:
            base_dir: Optional base directory to resolve relative paths against.

        Returns:
            Path: Absolute resolved path object.
        """
        path = Path(self.log_dir)
        if not path.is_absolute():
            root = base_dir or Path.cwd()
            path = (root / path).resolve()
        path.mkdir(parents=True, exist_ok=True)
        return path

    def get_absolute_storage_dir(self, base_dir: Optional[Path] = None) -> Path:
        """Resolve and ensure absolute path for uploaded raw files storage directory.

        Args:
            base_dir: Optional base directory to resolve relative paths against.

        Returns:
            Path: Absolute resolved path object.
        """
        path = Path(self.storage_dir)
        if not path.is_absolute():
            root = base_dir or Path.cwd()
            path = (root / path).resolve()
        path.mkdir(parents=True, exist_ok=True)
        return path


@lru_cache()
def get_settings() -> Settings:
    """Instantiate and cache application settings singleton instance.

    Returns:
        Settings: Validated global configuration object.
    """
    return Settings()
