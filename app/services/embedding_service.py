"""Embedding generation via OpenAI."""

from openai import OpenAI

from app.core.config import settings


def _get_client() -> OpenAI | None:
    if not settings.OPENAI_API_KEY:
        return None
    return OpenAI(api_key=settings.OPENAI_API_KEY)


def get_embedding(text: str) -> list[float]:
    """Get embedding for a single text."""
    client = _get_client()
    if not client:
        raise ValueError("OPENAI_API_KEY not configured")
    response = client.embeddings.create(input=[text], model=settings.EMBEDDING_MODEL)
    return response.data[0].embedding


def get_embeddings(texts: list[str]) -> list[list[float]]:
    """Get embeddings for multiple texts (batched)."""
    client = _get_client()
    if not client:
        raise ValueError("OPENAI_API_KEY not configured")
    response = client.embeddings.create(input=texts, model=settings.EMBEDDING_MODEL)
    return [d.embedding for d in sorted(response.data, key=lambda x: x.index)]
