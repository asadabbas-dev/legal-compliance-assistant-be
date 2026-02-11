"""OpenAI LLM generation for RAG answers."""

from openai import OpenAI

from app.core.config import settings
from app.services.llm_prompts import RAG_SYSTEM_PROMPT


def _get_client() -> OpenAI | None:
    if not settings.OPENAI_API_KEY:
        return None
    return OpenAI(api_key=settings.OPENAI_API_KEY)


def generate_answer_openai(
    question: str,
    context_chunks: list[dict],
    memory_messages: list[dict],
) -> str:
    """Generate answer from retrieved context using OpenAI."""
    client = _get_client()
    if not client:
        raise ValueError("OPENAI_API_KEY not configured")

    context_text = "\n\n---\n\n".join(
        f"[doc={c['document']}, page={c['page']}, section={c.get('section')}, chunk_id={c.get('chunk_id')}]\n{c['content']}"
        for c in context_chunks
    )
    memory_text = "\n".join(
        f"{m.get('role', 'user')}: {m.get('content', '')}" for m in memory_messages
    )

    messages = [
        {"role": "system", "content": RAG_SYSTEM_PROMPT},
        {
            "role": "user",
            "content": (
                f"Conversation memory:\n{memory_text}\n\n"
                f"Retrieved context:\n{context_text}\n\n"
                f"Question: {question}\n\n"
                "Answer based ONLY on retrieved context."
            ),
        },
    ]

    response = client.chat.completions.create(
        model=settings.OPENAI_MODEL,
        messages=messages,
        temperature=0,
    )
    return response.choices[0].message.content
