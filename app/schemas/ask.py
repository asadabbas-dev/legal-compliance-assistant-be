"""Ask/chat API schemas."""

from pydantic import BaseModel, Field


class AskRequest(BaseModel):
    """Request for POST /ask."""

    question: str = Field(..., min_length=1, description="User question")


class CitationSchema(BaseModel):
    """Source citation for an answer."""

    document: str
    page: int
    snippet: str | None = None


class AskResponse(BaseModel):
    """Response for POST /ask."""

    answer: str
    citations: list[CitationSchema]
