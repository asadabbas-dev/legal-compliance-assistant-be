"""Direct RAG query endpoint (without chat persistence)."""

from fastapi import APIRouter, Depends
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.auth.deps import get_optional_current_user
from app.models import User
from app.schemas.rag import RAGQueryRequest, RAGQueryResponse
from app.services.rag_service import query_rag
from app.services.user_service import get_or_create_anonymous_user

router = APIRouter(prefix="/rag", tags=["rag"])


@router.post("/query", response_model=RAGQueryResponse)
def rag_query(
    body: RAGQueryRequest,
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_optional_current_user),
):
    actor = current_user or get_or_create_anonymous_user(db)
    try:
        result = query_rag(db, user_id=actor.id, question=body.question)
    except Exception as exc:
        text = str(exc).lower()
        if "insufficient_quota" in text or "rate limit" in text or "ratelimiterror" in text:
            raise HTTPException(
                status_code=503,
                detail="AI service quota exceeded. Please add billing/credits for your OpenAI account.",
            ) from exc
        raise HTTPException(status_code=500, detail="Failed to process RAG query") from exc
    return RAGQueryResponse(
        answer=result.answer,
        citations=[
            {
                "document": c.document,
                "page": c.page,
                "section": c.section,
                "chunk_id": c.chunk_id,
                "similarity_score": c.similarity_score,
                "snippet": c.snippet,
            }
            for c in result.citations
        ],
        confidence_score=result.confidence_score,
    )
