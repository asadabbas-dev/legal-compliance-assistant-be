"""LLM generation for RAG answers. Supports OpenAI and Anthropic."""

from app.core.config import settings
from app.services.llm_openai import generate_answer_openai


def generate_answer(question: str, context_chunks: list[dict]) -> str:
    """Generate answer from retrieved context using configured LLM provider."""
    provider = (settings.LLM_PROVIDER or "openai").lower()

    if provider == "anthropic":
        from app.services.llm_anthropic import generate_answer_anthropic
        return generate_answer_anthropic(question, context_chunks)
    return generate_answer_openai(question, context_chunks)
