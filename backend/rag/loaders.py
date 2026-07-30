"""Modular document loading and text extraction engine.

Supports PDF, DOCX, and TXT document formats with page-level metadata parsing.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Type

import docx
import pypdf
from backend.logging.logger import get_logger

logger = get_logger(__name__)


@dataclass
class DocumentPage:
    """Dataclass storing extracted page text along with structural metadata."""

    page_number: int
    text: str
    document_name: str
    total_pages: int
    extra_metadata: Dict[str, str]


class BaseDocumentLoader(ABC):
    """Abstract base class for all file format document loaders."""

    def __init__(self, file_path: Path):
        """Initialize document loader with target file path.

        Args:
            file_path: Absolute or relative Path object pointing to target document.
        """
        self.file_path = Path(file_path)
        if not self.file_path.exists():
            raise FileNotFoundError(f"Target document does not exist: {self.file_path}")

    @abstractmethod
    def load(self) -> List[DocumentPage]:
        """Extract pages and text content from document.

        Returns:
            List[DocumentPage]: List of extracted document page objects.
        """
        pass


class PDFDocumentLoader(BaseDocumentLoader):
    """Document loader for Portable Document Format (.pdf) files."""

    def load(self) -> List[DocumentPage]:
        """Extract pages and text content from PDF file using PyPDF.

        Returns:
            List[DocumentPage]: Extracted PDF pages.
        """
        pages: List[DocumentPage] = []
        doc_name = self.file_path.name

        try:
            reader = pypdf.PdfReader(str(self.file_path))
            total_pages = len(reader.pages)

            for idx, page in enumerate(reader.pages, start=1):
                extracted_text = page.extract_text() or ""
                cleaned_text = extracted_text.strip()
                if cleaned_text:
                    pages.append(
                        DocumentPage(
                            page_number=idx,
                            text=cleaned_text,
                            document_name=doc_name,
                            total_pages=total_pages,
                            extra_metadata={"file_type": "pdf"},
                        )
                    )
            logger.info(
                f"Successfully parsed PDF document '{doc_name}' with {len(pages)} valid text pages out of {total_pages} total pages."
            )
            return pages
        except Exception as err:
            logger.error(f"Error loading PDF document '{doc_name}': {str(err)}", exc_info=True)
            raise ValueError(f"Failed to parse PDF document: {str(err)}") from err


class DocxDocumentLoader(BaseDocumentLoader):
    """Document loader for Microsoft Word (.docx) files."""

    def load(self) -> List[DocumentPage]:
        """Extract text content from Word DOCX file.

        Word documents are grouped logically by paragraphs into a single page representation
        or separated by explicit page breaks.

        Returns:
            List[DocumentPage]: Extracted DOCX content pages.
        """
        doc_name = self.file_path.name
        pages: List[DocumentPage] = []

        try:
            doc = docx.Document(str(self.file_path))
            paragraphs = [p.text.strip() for p in doc.paragraphs if p.text.strip()]
            full_text = "\n\n".join(paragraphs)

            if full_text:
                pages.append(
                    DocumentPage(
                        page_number=1,
                        text=full_text,
                        document_name=doc_name,
                        total_pages=1,
                        extra_metadata={"file_type": "docx"},
                    )
                )
            logger.info(f"Successfully parsed DOCX document '{doc_name}'.")
            return pages
        except Exception as err:
            logger.error(f"Error loading DOCX document '{doc_name}': {str(err)}", exc_info=True)
            raise ValueError(f"Failed to parse DOCX document: {str(err)}") from err


class TxtDocumentLoader(BaseDocumentLoader):
    """Document loader for plain text (.txt) files."""

    def load(self) -> List[DocumentPage]:
        """Extract text content from plain text UTF-8 file.

        Returns:
            List[DocumentPage]: Extracted text file page object.
        """
        doc_name = self.file_path.name
        pages: List[DocumentPage] = []

        try:
            with open(self.file_path, "r", encoding="utf-8", errors="replace") as f:
                content = f.read().strip()

            if content:
                pages.append(
                    DocumentPage(
                        page_number=1,
                        text=content,
                        document_name=doc_name,
                        total_pages=1,
                        extra_metadata={"file_type": "txt"},
                    )
                )
            logger.info(f"Successfully parsed TXT document '{doc_name}'.")
            return pages
        except Exception as err:
            logger.error(f"Error loading TXT document '{doc_name}': {str(err)}", exc_info=True)
            raise ValueError(f"Failed to parse TXT document: {str(err)}") from err


LOADER_MAPPING: Dict[str, Type[BaseDocumentLoader]] = {
    ".pdf": PDFDocumentLoader,
    ".docx": DocxDocumentLoader,
    ".txt": TxtDocumentLoader,
}


def get_document_loader(file_path: Path) -> BaseDocumentLoader:
    """Factory function instantiating appropriate DocumentLoader based on file extension.

    Args:
        file_path: Target document Path.

    Returns:
        BaseDocumentLoader: Concrete loader instance.

    Raises:
        ValueError: If file extension is unsupported.
    """
    ext = file_path.suffix.lower()
    if ext not in LOADER_MAPPING:
        raise ValueError(
            f"Unsupported document file format '{ext}'. Supported formats are: {list(LOADER_MAPPING.keys())}"
        )
    return LOADER_MAPPING[ext](file_path)
