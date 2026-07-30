"""Recursive text chunker for breaking document pages into overlapping passages.

Preserves sentence and paragraph context while managing strict character length limits.
"""

import hashlib
from dataclasses import dataclass, field
from typing import Dict, List, Any

from backend.rag.loaders import DocumentPage
from backend.logging.logger import get_logger

logger = get_logger(__name__)


@dataclass
class DocumentChunk:
    """Dataclass holding individual text chunk content and vector storage metadata."""

    chunk_id: str
    text: str
    document_name: str
    page_number: int
    chunk_index: int
    metadata: Dict[str, Any] = field(default_factory=dict)


class TextChunker:
    """Recursive character-based text splitter with semantic separator prioritization."""

    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 50):
        """Initialize chunker with target size and overlap parameters.

        Args:
            chunk_size: Maximum character count per chunk.
            chunk_overlap: Overlapping character count between consecutive chunks.
        """
        if chunk_overlap >= chunk_size:
            raise ValueError("chunk_overlap must be strictly less than chunk_size")

        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        # Hierarchy of separators for natural sentence and paragraph boundaries
        self.separators = ["\n\n", "\n", ". ", "? ", "! ", "; ", " ", ""]

    def _generate_chunk_id(self, doc_name: str, page_num: int, chunk_idx: int, text: str) -> str:
        """Generate deterministic hash-based unique chunk identifier.

        Args:
            doc_name: Source document name.
            page_num: Page number.
            chunk_idx: Zero-based chunk index.
            text: Chunk text content.

        Returns:
            str: Unique chunk ID string.
        """
        raw_key = f"{doc_name}_p{page_num}_c{chunk_idx}_{text[:30]}"
        short_hash = hashlib.sha256(raw_key.encode("utf-8")).hexdigest()[:12]
        # Clean document name for safe ID formatting
        clean_doc = "".join(c if c.isalnum() else "_" for c in doc_name)
        return f"doc_{clean_doc}_p{page_num}_c{chunk_idx}_{short_hash}"

    def _split_text_recursively(self, text: str, separators: List[str]) -> List[str]:
        """Split text recursively using decreasing hierarchy of natural separators.

        Args:
            text: Input text block.
            separators: Remaining list of separators to split by.

        Returns:
            List[str]: List of text segments within length limits where possible.
        """
        if len(text) <= self.chunk_size:
            return [text]

        if not separators:
            # Fallback hard split if no separators remain
            chunks = []
            for i in range(0, len(text), self.chunk_size - self.chunk_overlap):
                chunks.append(text[i : i + self.chunk_size])
            return chunks

        sep = separators[0]
        remaining_seps = separators[1:]

        splits = text.split(sep) if sep != "" else list(text)
        final_passages: List[str] = []
        current_passage: List[str] = []
        current_len = 0

        for split in splits:
            split_text = split if sep == "" else split + sep
            if len(split_text) > self.chunk_size:
                # Store accumulated passage
                if current_passage:
                    final_passages.append("".join(current_passage).strip())
                    current_passage = []
                    current_len = 0
                # Recursively break oversized split
                sub_splits = self._split_text_recursively(split, remaining_seps)
                final_passages.extend(sub_splits)
            elif current_len + len(split_text) <= self.chunk_size:
                current_passage.append(split_text)
                current_len += len(split_text)
            else:
                final_passages.append("".join(current_passage).strip())
                current_passage = [split_text]
                current_len = len(split_text)

        if current_passage:
            final_passages.append("".join(current_passage).strip())

        return [p for p in final_passages if p]

    def _create_overlapping_chunks(self, passages: List[str]) -> List[str]:
        """Combine passages into target chunk size with configured overlap.

        Args:
            passages: List of atomic text passages.

        Returns:
            List[str]: List of text chunks matching overlap and size parameters.
        """
        chunks: List[str] = []
        current_chunk: List[str] = []
        current_length = 0

        for passage in passages:
            passage_str = passage.strip()
            if not passage_str:
                continue

            if current_length + len(passage_str) + 1 <= self.chunk_size:
                current_chunk.append(passage_str)
                current_length += len(passage_str) + 1
            else:
                if current_chunk:
                    full_chunk_text = " ".join(current_chunk)
                    chunks.append(full_chunk_text)

                    # Compute overlap buffer from trailing items
                    overlap_items: List[str] = []
                    overlap_len = 0
                    for item in reversed(current_chunk):
                        if overlap_len + len(item) + 1 <= self.chunk_overlap:
                            overlap_items.insert(0, item)
                            overlap_len += len(item) + 1
                        else:
                            break
                    current_chunk = overlap_items
                    current_length = sum(len(x) + 1 for x in current_chunk)

                current_chunk.append(passage_str)
                current_length += len(passage_str) + 1

        if current_chunk:
            chunks.append(" ".join(current_chunk))

        return chunks

    def chunk_document_pages(self, pages: List[DocumentPage]) -> List[DocumentChunk]:
        """Chunk a list of document pages into vector-ready DocumentChunk objects.

        Args:
            pages: List of loaded DocumentPage instances.

        Returns:
            List[DocumentChunk]: Created document chunk objects with metadata.
        """
        all_chunks: List[DocumentChunk] = []
        global_chunk_idx = 0

        for page in pages:
            raw_text = page.text.strip()
            if not raw_text:
                continue

            atomic_passages = self._split_text_recursively(raw_text, self.separators)
            page_chunk_texts = self._create_overlapping_chunks(atomic_passages)

            for chunk_idx, text_content in enumerate(page_chunk_texts):
                chunk_id = self._generate_chunk_id(
                    doc_name=page.document_name,
                    page_num=page.page_number,
                    chunk_idx=global_chunk_idx,
                    text=text_content,
                )

                chunk_metadata: Dict[str, Any] = {
                    "chunk_id": chunk_id,
                    "document_name": page.document_name,
                    "page_number": page.page_number,
                    "total_pages": page.total_pages,
                    "chunk_index": global_chunk_idx,
                    "char_length": len(text_content),
                    **page.extra_metadata,
                }

                all_chunks.append(
                    DocumentChunk(
                        chunk_id=chunk_id,
                        text=text_content,
                        document_name=page.document_name,
                        page_number=page.page_number,
                        chunk_index=global_chunk_idx,
                        metadata=chunk_metadata,
                    )
                )
                global_chunk_idx += 1

        logger.info(
            f"Chunked document '{pages[0].document_name if pages else 'unknown'}' into {len(all_chunks)} chunks (size={self.chunk_size}, overlap={self.chunk_overlap})."
        )
        return all_chunks
