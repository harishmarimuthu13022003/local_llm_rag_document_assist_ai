"""Local ChromaDB vector database manager for document chunk persistence and semantic search.
"""

import time
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import backend  # noqa: F401 - Initialize Windows App Control DLL bypass
import chromadb
from chromadb.config import Settings as ChromaSettings

from backend.config.settings import get_settings
from backend.logging.logger import get_logger
from backend.rag.chunker import DocumentChunk

logger = get_logger(__name__)


@dataclass
class VectorSearchResult:
    """Dataclass encapsulating retrieved similarity search matches."""

    chunk_id: str
    text: str
    document_name: str
    page_number: int
    score: float
    metadata: Dict[str, Any]


class ChromaVectorStore:
    """Manager class handling local ChromaDB persistent storage operations."""

    COLLECTION_NAME = "document_chunks"

    def __init__(self, chroma_path: Optional[str] = None) -> None:
        """Initialize persistent ChromaDB client and collection.

        Args:
            chroma_path: Path string override for Chroma storage directory.
        """
        settings = get_settings()
        target_path = chroma_path or str(settings.get_absolute_chroma_path())

        logger.info(f"Initializing persistent ChromaDB at path: '{target_path}'")
        self.client = chromadb.PersistentClient(
            path=target_path,
            settings=ChromaSettings(anonymized_telemetry=False, allow_reset=True),
        )

        self.collection = self.client.get_or_create_collection(
            name=self.COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"},
        )

    def add_chunks(self, chunks: List[DocumentChunk], embeddings: List[List[float]]) -> None:
        """Store document chunks and their corresponding embedding vectors into ChromaDB.

        Args:
            chunks: List of DocumentChunk dataclass instances.
            embeddings: List of matching float embedding vectors.
        """
        if not chunks or not embeddings:
            logger.warning("Empty chunks or embeddings array provided to add_chunks.")
            return

        if len(chunks) != len(embeddings):
            raise ValueError(
                f"Mismatch between chunks count ({len(chunks)}) and embeddings count ({len(embeddings)})"
            )

        ids: List[str] = []
        documents: List[str] = []
        metadatas: List[Dict[str, Any]] = []

        for chunk in chunks:
            ids.append(chunk.chunk_id)
            documents.append(chunk.text)
            # Ensure metadata values are serializable primitive types
            clean_meta = {
                "chunk_id": chunk.chunk_id,
                "document_name": chunk.document_name,
                "page_number": int(chunk.page_number),
                "chunk_index": int(chunk.chunk_index),
            }
            if "total_pages" in chunk.metadata:
                clean_meta["total_pages"] = int(chunk.metadata["total_pages"])
            if "file_type" in chunk.metadata:
                clean_meta["file_type"] = str(chunk.metadata["file_type"])
            metadatas.append(clean_meta)

        start_time = time.perf_counter()
        self.collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas,
        )
        elapsed_ms = (time.perf_counter() - start_time) * 1000
        logger.info(
            f"Successfully stored {len(chunks)} chunks in ChromaDB in {elapsed_ms:.2f}ms.",
            extra={"ingestion": True, "chunk_count": len(chunks)},
        )

    def similarity_search(
        self, query_embedding: List[float], top_k: int = 4
    ) -> List[VectorSearchResult]:
        """Perform cosine similarity search against stored document chunk vectors.

        Args:
            query_embedding: 384-dimensional query vector.
            top_k: Number of nearest matches to retrieve.

        Returns:
            List[VectorSearchResult]: Ranked list of search result matches.
        """
        start_time = time.perf_counter()

        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            include=["documents", "metadatas", "distances"],
        )

        elapsed_ms = (time.perf_counter() - start_time) * 1000
        logger.info(
            f"ChromaDB similarity search completed in {elapsed_ms:.2f}ms.",
            extra={"vector_search_latency_ms": elapsed_ms, "top_k": top_k},
        )

        search_results: List[VectorSearchResult] = []
        if not results or not results["ids"] or not results["ids"][0]:
            return search_results

        ids = results["ids"][0]
        documents = results["documents"][0] if results.get("documents") else []
        metadatas = results["metadatas"][0] if results.get("metadatas") else []
        distances = results["distances"][0] if results.get("distances") else []

        for idx in range(len(ids)):
            doc_text = documents[idx] if idx < len(documents) else ""
            meta = metadatas[idx] if idx < len(metadatas) else {}
            dist = distances[idx] if idx < len(distances) else 1.0
            # Convert cosine distance to similarity score
            similarity_score = max(0.0, 1.0 - float(dist))

            search_results.append(
                VectorSearchResult(
                    chunk_id=ids[idx],
                    text=doc_text,
                    document_name=meta.get("document_name", "Unknown"),
                    page_number=int(meta.get("page_number", 1)),
                    score=similarity_score,
                    metadata=meta,
                )
            )

        return search_results

    def list_documents(self) -> List[Dict[str, Any]]:
        """Fetch summary of all unique ingested documents stored in vector database.

        Returns:
            List[Dict[str, Any]]: Metadata list containing document name, total chunks, page count.
        """
        all_records = self.collection.get(include=["metadatas"])
        if not all_records or not all_records.get("metadatas"):
            return []

        doc_map: Dict[str, Dict[str, Any]] = {}
        for meta in all_records["metadatas"]:
            doc_name = meta.get("document_name", "Unknown")
            page_num = int(meta.get("page_number", 1))
            file_type = meta.get("file_type", "unknown")

            if doc_name not in doc_map:
                doc_map[doc_name] = {
                    "document_name": doc_name,
                    "chunk_count": 0,
                    "max_page": page_num,
                    "file_type": file_type,
                }

            doc_map[doc_name]["chunk_count"] += 1
            if page_num > doc_map[doc_name]["max_page"]:
                doc_map[doc_name]["max_page"] = page_num

        return list(doc_map.values())

    def get_document_chunks(self, document_name: str) -> List[Dict[str, Any]]:
        """Retrieve all chunk records belonging to a specific document name.

        Args:
            document_name: Target document filename.

        Returns:
            List[Dict[str, Any]]: Document chunks with text and metadata.
        """
        records = self.collection.get(
            where={"document_name": document_name},
            include=["documents", "metadatas"],
        )

        chunks: List[Dict[str, Any]] = []
        if not records or not records.get("ids"):
            return chunks

        for idx in range(len(records["ids"])):
            meta = records["metadatas"][idx] if records.get("metadatas") else {}
            doc_text = records["documents"][idx] if records.get("documents") else ""

            chunks.append(
                {
                    "chunk_id": records["ids"][idx],
                    "text": doc_text,
                    "document_name": meta.get("document_name", document_name),
                    "page_number": int(meta.get("page_number", 1)),
                    "chunk_index": int(meta.get("chunk_index", 0)),
                    "metadata": meta,
                }
            )

        # Sort chunks by page number and chunk index
        chunks.sort(key=lambda c: (c["page_number"], c["chunk_index"]))
        return chunks

    def delete_document(self, document_name: str) -> int:
        """Delete all chunks associated with a specific document.

        Args:
            document_name: Document filename to remove.

        Returns:
            int: Number of deleted chunk records.
        """
        existing = self.collection.get(where={"document_name": document_name})
        if not existing or not existing.get("ids"):
            return 0

        ids_to_delete = existing["ids"]
        self.collection.delete(ids=ids_to_delete)
        logger.info(f"Deleted {len(ids_to_delete)} vector chunks for document '{document_name}'.")
        return len(ids_to_delete)
