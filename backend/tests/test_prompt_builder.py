"""Unit tests for prompt builder and zero-hallucination instruction enforcement."""

from backend.rag.prompt_builder import FALLBACK_ANSWER, PromptBuilder
from backend.rag.vectorstore import VectorSearchResult


def test_prompt_builder_with_results():
    """Verify prompt formatting when context passages are present."""
    builder = PromptBuilder(max_context_chars=1000)

    results = [
        VectorSearchResult(
            chunk_id="chk_101",
            text="The project budget is $500,000.",
            document_name="financial_report.pdf",
            page_number=3,
            score=0.92,
            metadata={},
        )
    ]

    prompt = builder.build_prompt(question="What is the project budget?", retrieved_results=results)

    assert "DOCUMENT CONTEXT:" in prompt
    assert "financial_report.pdf" in prompt
    assert "The project budget is $500,000." in prompt
    assert "USER QUESTION: What is the project budget?" in prompt
    assert FALLBACK_ANSWER in prompt


def test_prompt_builder_empty_results():
    """Verify fallback context placeholder when no passages are retrieved."""
    builder = PromptBuilder()

    prompt = builder.build_prompt(question="Who won the race?", retrieved_results=[])

    assert "No relevant document passages found." in prompt
    assert FALLBACK_ANSWER in prompt
