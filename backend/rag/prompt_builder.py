"""Prompt engineering module enforcing strict context-grounded response generation.

Prevents model hallucination by embedding explicit document citations and fallbacks.
"""

from typing import List
from backend.config.settings import get_settings
from backend.logging.logger import get_logger
from backend.rag.vectorstore import VectorSearchResult

logger = get_logger(__name__)

FALLBACK_ANSWER = "I don't know based on the provided documents."

SYSTEM_DIRECTIVE = (
    "You are an authoritative, detailed, and beautifully structured document assistant.\n"
    "Answer the user's question with COMPLETE, EXHAUSTIVE detail and ELEGANT STRUCTURE using ONLY the provided document context below.\n\n"
    "CRITICAL FORMATTING & STRUCTURE INSTRUCTIONS:\n"
    "1. BEAUTIFUL STRUCTURED LAYOUT: Format your response using clean, elegant Markdown:\n"
    "   - Start with a bold main title (e.g. **Phase X: Title**)\n"
    "   - Use sub-headers with underline dividers (e.g. ### Overview \\n ---------------\\n)\n"
    "   - Use bullet points with bold item names followed by detailed explanations (e.g. * **Feature Name**: Detailed explanation)\n"
    "   - Use Markdown tables for roadmaps or structured comparisons when applicable.\n"
    "2. EXHAUSTIVE COMPLETENESS: Retrieve and present ALL relevant information, Overview, Goals, Features, Integrations, Infrastructure, Target Users, and Next Steps from the document context. Do NOT skip, omit, or summarize items from lists.\n"
    "3. STRICT GROUNDING: If the answer cannot be determined strictly from the provided context passages, reply with EXACTLY:\n"
    f'"{FALLBACK_ANSWER}"\n'
    "4. NO OUTSIDE KNOWLEDGE: Do NOT use external knowledge or make assumptions not directly stated in the context."
)


class PromptBuilder:
    """Prompt builder constructing grounded system prompts and user query payloads."""

    def __init__(self, max_context_chars: int = 3000):
        """Initialize prompt builder with maximum context token/character limits.

        Args:
            max_context_chars: Maximum character length allowed for combined context.
        """
        settings = get_settings()
        self.max_context_chars = max_context_chars or settings.max_context

    def build_prompt(self, question: str, retrieved_results: List[VectorSearchResult]) -> str:
        """Construct prompt embedding retrieved passages with structural citation headers.

        Args:
            question: User natural language query.
            retrieved_results: List of VectorSearchResult instances.

        Returns:
            str: Complete prompt string ready for LLM inference.
        """
        if not retrieved_results:
            logger.info("No retrieved chunks provided to prompt builder.")
            context_text = "No relevant document passages found."
        else:
            context_passages: List[str] = []
            total_chars = 0

            for idx, res in enumerate(retrieved_results, start=1):
                header = f"[Source {idx}: Document='{res.document_name}', Page={res.page_number}, ChunkID='{res.chunk_id}']"
                passage_block = f"{header}\n{res.text.strip()}\n"

                if total_chars + len(passage_block) > self.max_context_chars:
                    logger.warning(
                        f"Context truncated at passage {idx} due to max_context limit ({self.max_context_chars} chars)."
                    )
                    break

                context_passages.append(passage_block)
                total_chars += len(passage_block)

            context_text = "\n---\n".join(context_passages)

        full_prompt = (
            f"{SYSTEM_DIRECTIVE}\n\n"
            f"DOCUMENT CONTEXT:\n"
            f"----------------------------------------\n"
            f"{context_text}\n"
            f"----------------------------------------\n\n"
            f"USER QUESTION: {question}\n\n"
            f"GROUNDED ANSWER:"
        )

        return full_prompt
