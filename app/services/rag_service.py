"""RAG retrieval + generation service."""

from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from sqlalchemy.orm import Session

from app.core.config import settings
from app.models import ChatMessage, Document, DocumentChunk
from app.services.embedding_service import get_embedding
from app.services.llm_service import generate_answer


@dataclass
class Citation:
    document: str
    page: int
    section: str | None
    chunk_id: int
    similarity_score: float
    snippet: str


@dataclass
class RAGResult:
    answer: str
    citations: list[Citation]
    confidence_score: float


def _distance_to_similarity(distance: float) -> float:
    return max(0.0, min(1.0, 1.0 - float(distance)))


def get_chat_memory(db: Session, chat_id, max_messages: int) -> list[dict]:
    rows = (
        db.query(ChatMessage)
        .filter(ChatMessage.chat_id == chat_id)
        .order_by(ChatMessage.created_at.desc())
        .limit(max_messages)
        .all()
    )
    rows.reverse()
    return [{"role": r.role, "content": r.content} for r in rows]


def query_rag(
    db: Session,
    *,
    user_id: UUID,
    question: str,
    chat_id=None,
    top_k: int | None = None,
) -> RAGResult:
    k = top_k or settings.TOP_K
    query_embedding = get_embedding(question)

    rows = (
        db.query(
            DocumentChunk,
            Document.filename,
            DocumentChunk.embedding.cosine_distance(query_embedding).label("distance"),
        )
        .join(Document, Document.id == DocumentChunk.document_id)
        .filter(DocumentChunk.user_id == user_id)
        .order_by(DocumentChunk.embedding.cosine_distance(query_embedding))
        .limit(k)
        .all()
    )

    if not rows:
        return RAGResult(
            answer="Not found in uploaded documents",
            citations=[],
            confidence_score=0.0,
        )

    context_chunks = []
    citations: list[Citation] = []
    for chunk, filename, distance in rows:
        similarity = _distance_to_similarity(distance)
        context_chunks.append(
            {
                "document": filename,
                "page": chunk.page_number,
                "section": chunk.section,
                "chunk_id": chunk.id,
                "content": chunk.chunk_text,
            }
        )
        citations.append(
            Citation(
                document=filename,
                page=chunk.page_number,
                section=chunk.section,
                chunk_id=chunk.id,
                similarity_score=round(similarity, 4),
                snippet=(chunk.chunk_text or "")[:500],
            )
        )

    memory_messages = get_chat_memory(db, chat_id, settings.MAX_CHAT_MEMORY_MESSAGES) if chat_id else []
    answer = generate_answer(question=question, context_chunks=context_chunks, memory_messages=memory_messages)
    confidence = sum(c.similarity_score for c in citations) / len(citations)
    return RAGResult(answer=answer, citations=citations, confidence_score=round(confidence, 4))
