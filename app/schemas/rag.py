"""RAG query response schemas."""

from pydantic import BaseModel, Field


class RAGQueryRequest(BaseModel):
    question: str = Field(..., min_length=1)


class RAGCitation(BaseModel):
    document: str
    page: int
    section: str | None = None
    chunk_id: int
    similarity_score: float
    snippet: str


class RAGQueryResponse(BaseModel):
    answer: str
    citations: list[RAGCitation]
    confidence_score: float
