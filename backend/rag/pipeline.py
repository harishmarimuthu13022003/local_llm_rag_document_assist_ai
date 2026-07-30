"""RAG Pipeline Orchestrator integrating document ingestion, vector retrieval, prompt building, and local LLM execution.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

from backend.config.settings import get_settings
from backend.logging.logger import get_logger
from backend.rag.chunker import TextChunker
from backend.rag.embeddings import EmbeddingGenerator
from backend.rag.llm_client import OllamaLLMClient
from backend.rag.loaders import get_document_loader
from backend.rag.prompt_builder import FALLBACK_ANSWER, PromptBuilder
from backend.rag.vectorstore import ChromaVectorStore, VectorSearchResult

logger = get_logger(__name__)


@dataclass
class SourceCitation:
    """Dataclass holding structured citation information for front-end rendering."""

    document_name: str
    page_number: int
    chunk_id: str
    score: float
    snippet: str


@dataclass
class RAGQueryResponse:
    """Dataclass encapsulating final RAG response answer, citations, and latency metrics."""

    answer: str
    confidence: Optional[float]
    sources: List[SourceCitation]
    retrieved_chunks: List[Dict[str, Any]]
    metrics: Dict[str, float] = field(default_factory=dict)


class RAGPipeline:
    """Master RAG pipeline coordinator service."""

    def __init__(
        self,
        vector_store: Optional[ChromaVectorStore] = None,
        embedding_generator: Optional[EmbeddingGenerator] = None,
        llm_client: Optional[OllamaLLMClient] = None,
    ):
        """Initialize RAG pipeline dependencies.

        Args:
            vector_store: ChromaVectorStore instance.
            embedding_generator: EmbeddingGenerator instance.
            llm_client: OllamaLLMClient instance.
        """
        settings = get_settings()
        self.settings = settings
        self.vector_store = vector_store or ChromaVectorStore()
        self.embedding_generator = embedding_generator or EmbeddingGenerator()
        self.llm_client = llm_client or OllamaLLMClient()
        self.chunker = TextChunker(
            chunk_size=settings.chunk_size,
            chunk_overlap=settings.chunk_overlap,
        )
        self.prompt_builder = PromptBuilder(max_context_chars=settings.max_context)

    def ingest_document(self, file_path: Path) -> Dict[str, Any]:
        """Execute document ingestion workflow: parse -> chunk -> embed -> store.

        Args:
            file_path: Path to target document file (PDF, DOCX, TXT).

        Returns:
            Dict[str, Any]: Ingestion summary dict containing chunk count and document name.
        """
        logger.info(f"Starting document ingestion pipeline for file: '{file_path.name}'")

        # Step 1: Load Document Pages
        loader = get_document_loader(file_path)
        pages = loader.load()

        if not pages:
            raise ValueError(f"No extractable text content found in document '{file_path.name}'")

        # Step 2: Chunk Document
        chunks = self.chunker.chunk_document_pages(pages)

        # Step 3: Generate Embeddings
        chunk_texts = [c.text for c in chunks]
        embeddings = self.embedding_generator.embed_documents(chunk_texts)

        # Step 4: Persist to Vector Store
        self.vector_store.add_chunks(chunks, embeddings)

        return {
            "document_name": file_path.name,
            "total_pages": len(pages),
            "total_chunks": len(chunks),
            "status": "success",
        }

    async def answer_question(
        self, question: str, top_k: Optional[int] = None
    ) -> RAGQueryResponse:
        """Execute RAG question-answering workflow: embed -> retrieve -> prompt -> LLM.

        Args:
            question: Natural language user question.
            top_k: Top-K context chunk count override.

        Returns:
            RAGQueryResponse: Structured response with answer, citations, and metrics.
        """
        k = top_k or self.settings.top_k
        logger.info(f"Processing RAG query: '{question}' (Top-K={k})")

        metrics: Dict[str, float] = {}

        # Step 1: Embed Query
        query_vector = self.embedding_generator.embed_text(question)

        # Step 2: Retrieve Top-K Chunks
        search_results: List[VectorSearchResult] = self.vector_store.similarity_search(
            query_embedding=query_vector,
            top_k=k,
        )

        # Build Citations and Chunk Previews
        citations: List[SourceCitation] = []
        raw_chunks: List[Dict[str, Any]] = []
        max_score = 0.0

        for res in search_results:
            if res.score > max_score:
                max_score = res.score

            citations.append(
                SourceCitation(
                    document_name=res.document_name,
                    page_number=res.page_number,
                    chunk_id=res.chunk_id,
                    score=round(res.score, 4),
                    snippet=res.text[:200] + "..." if len(res.text) > 200 else res.text,
                )
            )

            raw_chunks.append(
                {
                    "chunk_id": res.chunk_id,
                    "document_name": res.document_name,
                    "page_number": res.page_number,
                    "score": round(res.score, 4),
                    "text": res.text,
                    "metadata": res.metadata,
                }
            )

        # Step 3: Handle empty or low-relevance retrieval cases
        if not search_results or max_score < 0.15:
            logger.info(
                f"Retrieved chunks below confidence threshold (max_score={max_score:.4f}). Returning fallback."
            )
            return RAGQueryResponse(
                answer=FALLBACK_ANSWER,
                confidence=round(max_score, 4),
                sources=[],
                retrieved_chunks=raw_chunks,
                metrics={"llm_latency_ms": 0.0},
            )

        # Step 4: Construct Grounded Prompt
        prompt = self.prompt_builder.build_prompt(
            question=question,
            retrieved_results=search_results,
        )

        # Step 5: Call Local LLM via Ollama
        try:
            llm_res = await self.llm_client.generate_answer(prompt)
            answer_text = llm_res.get("answer", "").strip()
            metrics["llm_latency_ms"] = llm_res.get("latency_ms", 0.0)

            if not answer_text or FALLBACK_ANSWER.lower() in answer_text.lower():
                answer_text = FALLBACK_ANSWER

        except Exception as err:
            logger.error(f"LLM execution error during query processing: {str(err)}")
            answer_text = f"An error occurred while generating answer from local LLM: {str(err)}"

        return RAGQueryResponse(
            answer=answer_text,
            confidence=round(max_score, 4),
            sources=citations,
            retrieved_chunks=raw_chunks,
            metrics=metrics,
        )
