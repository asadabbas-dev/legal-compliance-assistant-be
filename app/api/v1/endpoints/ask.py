"""Ask question endpoint - RAG Q&A."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.core.config import settings
from app.models import Chunk, Document
from app.schemas.ask import AskRequest, AskResponse, CitationSchema
from app.services.embedding_service import get_embedding
from app.services.llm_service import generate_answer

router = APIRouter(prefix="/ask", tags=["ask"])

NO_DOCUMENTS_MESSAGE = (
    "No documents have been uploaded yet. Please upload PDF documents first."
)


@router.post("", response_model=AskResponse)
def ask_question(
    body: AskRequest,
    db: Session = Depends(get_db),
):
    """Ask a question and get answer with citations."""
    question = body.question.strip()

    query_embedding = get_embedding(question)

    chunks = (
        db.query(Chunk, Document.filename)
        .join(Document, Chunk.document_id == Document.id)
        .order_by(Chunk.embedding.cosine_distance(query_embedding))
        .limit(settings.TOP_K)
        .all()
    )

    if not chunks:
        return AskResponse(answer=NO_DOCUMENTS_MESSAGE, citations=[])

    context_chunks = [
        {"document": filename, "page": chunk.page_number, "content": chunk.content}
        for chunk, filename in chunks
    ]

    answer = generate_answer(question, context_chunks)

    seen = set()
    unique_citations = []
    for c in context_chunks:
        key = (c["document"], c["page"])
        if key not in seen:
            seen.add(key)
            snippet = c.get("content", "")[:500] if c.get("content") else None
            unique_citations.append(
                CitationSchema(
                    document=c["document"],
                    page=c["page"],
                    snippet=snippet,
                )
            )

    return AskResponse(answer=answer, citations=unique_citations)
