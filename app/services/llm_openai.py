"""OpenAI LLM generation for RAG answers."""

from openai import OpenAI

from app.core.config import settings
from app.services.llm_prompts import RAG_SYSTEM_PROMPT


def _get_client() -> OpenAI | None:
    if not settings.OPENAI_API_KEY:
        return None
    return OpenAI(api_key=settings.OPENAI_API_KEY)


def generate_answer_openai(question: str, context_chunks: list[dict]) -> str:
    """Generate answer from retrieved context using OpenAI."""
    client = _get_client()
    if not client:
        raise ValueError("OPENAI_API_KEY not configured")

    context_text = "\n\n---\n\n".join(
        f"[Document: {c['document']}, Page: {c['page']}]\n{c['content']}"
        for c in context_chunks
    )

    messages = [
        {"role": "system", "content": RAG_SYSTEM_PROMPT},
        {
            "role": "user",
            "content": f"Context:\n{context_text}\n\nQuestion: {question}\n\nAnswer (with citations):",
        },
    ]

    response = client.chat.completions.create(
        model=settings.OPENAI_MODEL,
        messages=messages,
        temperature=0,
    )
    return response.choices[0].message.content
