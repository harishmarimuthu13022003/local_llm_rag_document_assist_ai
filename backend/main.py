"""FastAPI Application Main Entry Point.

Configures CORS, global exception handlers, structured logging, and registers API routers.
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

import uvicorn
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

import backend  # noqa: F401 - Initialize Windows App Control DLL bypass
from backend.api.routers import chat, documents, health, ingest
from backend.config.settings import get_settings
from backend.logging.logger import get_logger, setup_logging

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Lifespan context manager for application startup and shutdown tasks."""
    setup_logging()
    settings = get_settings()
    logger.info("=" * 60)
    logger.info("Starting Local LLM Document Q&A Chatbot Backend API Service")
    logger.info(f"Ollama Server Host : {settings.ollama_host}")
    logger.info(f"Target LLM Model   : {settings.ollama_model}")
    logger.info(f"Embedding Model    : {settings.embedding_model}")
    logger.info(f"Chroma Storage Path: {settings.get_absolute_chroma_path()}")
    logger.info(f"Server Listening   : http://{settings.host}:{settings.port}")
    logger.info("=" * 60)
    yield
    logger.info("Shutting down Local LLM Document Q&A Chatbot Backend service...")


app = FastAPI(
    title="Local LLM Document Q&A Chatbot (RAG API)",
    description=(
        "Production-Grade MVP RAG system powered by local Ollama (llama3.2:3b), "
        "SentenceTransformers (all-MiniLM-L6-v2), and ChromaDB."
    ),
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configure CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Production setup allows local React/Vite origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Catch-all global exception handler ensuring structured JSON error reporting."""
    logger.error(f"Global uncaught exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "An unexpected internal server error occurred.",
            "error_type": exc.__class__.__name__,
            "message": str(exc),
        },
    )


# Register API Routers
app.include_router(health.router)
app.include_router(ingest.router)
app.include_router(chat.router)
app.include_router(documents.router)


if __name__ == "__main__":
    settings = get_settings()
    uvicorn.run(
        "backend.main:app",
        host=settings.host,
        port=settings.port,
        reload=False,
        log_level=settings.log_level.lower(),
    )
