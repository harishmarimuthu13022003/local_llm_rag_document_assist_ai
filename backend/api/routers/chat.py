"""Chat API router (POST /chat)."""

from fastapi import APIRouter, Depends, HTTPException, status

from backend.api.dependencies import get_rag_pipeline_dep
from backend.logging.logger import get_logger
from backend.rag.pipeline import RAGPipeline
from backend.schemas.chat import (
    ChatRequest,
    ChatResponse,
    RetrievedChunkSchema,
    SourceCitationSchema,
)

logger = get_logger(__name__)
router = APIRouter(tags=["RAG Chat"])


@router.post(
    "/chat",
    response_model=ChatResponse,
    summary="Submit Question for Grounded RAG Answer",
    description="Embeds question, performs vector similarity search, constructs grounded prompt, invokes local Ollama LLM, and returns grounded answer with citations.",
)
async def chat_query(
    request: ChatRequest,
    pipeline: RAGPipeline = Depends(get_rag_pipeline_dep),
) -> ChatResponse:
    """Process user question through RAG pipeline and return grounded response."""
    question = request.question.strip()
    if not question:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Question query string cannot be blank.",
        )

    logger.info(f"API received chat query: '{question}'", extra={"api_request": True})

    try:
        rag_response = await pipeline.answer_question(
            question=question,
            top_k=request.top_k,
        )

        sources_schema = [
            SourceCitationSchema(
                document_name=src.document_name,
                page_number=src.page_number,
                chunk_id=src.chunk_id,
                score=src.score,
                snippet=src.snippet,
            )
            for src in rag_response.sources
        ]

        chunks_schema = [
            RetrievedChunkSchema(
                chunk_id=c["chunk_id"],
                document_name=c["document_name"],
                page_number=c["page_number"],
                score=c["score"],
                text=c["text"],
                metadata=c["metadata"],
            )
            for c in rag_response.retrieved_chunks
        ]

        return ChatResponse(
            answer=rag_response.answer,
            confidence=rag_response.confidence,
            sources=sources_schema,
            retrieved_chunks=chunks_schema,
            metrics=rag_response.metrics,
        )

    except Exception as err:
        logger.error(f"Error processing chat query: {str(err)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process chat query: {str(err)}",
        ) from err
