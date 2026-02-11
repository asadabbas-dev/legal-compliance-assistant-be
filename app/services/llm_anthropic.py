"""Anthropic Claude LLM generation for RAG answers."""

from anthropic import Anthropic

from app.core.config import settings
from app.services.llm_prompts import RAG_SYSTEM_PROMPT


def _get_client() -> Anthropic | None:
    if not settings.ANTHROPIC_API_KEY:
        return None
    return Anthropic(api_key=settings.ANTHROPIC_API_KEY)


def generate_answer_anthropic(
    question: str,
    context_chunks: list[dict],
    memory_messages: list[dict],
) -> str:
    """Generate answer from retrieved context using Anthropic Claude."""
    client = _get_client()
    if not client:
        raise ValueError("ANTHROPIC_API_KEY not configured")

    context_text = "\n\n---\n\n".join(
        f"[doc={c['document']}, page={c['page']}, section={c.get('section')}, chunk_id={c.get('chunk_id')}]\n{c['content']}"
        for c in context_chunks
    )
    memory_text = "\n".join(
        f"{m.get('role', 'user')}: {m.get('content', '')}" for m in memory_messages
    )

    user_content = (
        f"Conversation memory:\n{memory_text}\n\n"
        f"Retrieved context:\n{context_text}\n\n"
        f"Question: {question}\n\n"
        "Answer based ONLY on retrieved context."
    )

    response = client.messages.create(
        model=settings.ANTHROPIC_MODEL,
        max_tokens=2048,
        system=RAG_SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_content}],
    )

    if response.content and len(response.content) > 0:
        block = response.content[0]
        if hasattr(block, "text"):
            return block.text
    return ""
