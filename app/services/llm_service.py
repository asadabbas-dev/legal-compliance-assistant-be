"""LLM answer generation with provider routing."""

from app.core.config import settings
from app.services.llm_openai import generate_answer_openai


def generate_answer(
    *,
    question: str,
    context_chunks: list[dict],
    memory_messages: list[dict] | None = None,
) -> str:
    """Generate an answer from retrieved context with optional memory snippets."""
    provider = (settings.LLM_PROVIDER or "openai").lower()

    if provider == "anthropic":
        from app.services.llm_anthropic import generate_answer_anthropic
        return generate_answer_anthropic(question, context_chunks, memory_messages or [])
    return generate_answer_openai(question, context_chunks, memory_messages or [])
