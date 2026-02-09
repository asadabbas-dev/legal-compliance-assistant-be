"""Feedback API schemas."""

from pydantic import BaseModel, Field, field_validator


class FeedbackRequest(BaseModel):
    """Request for POST /feedback."""

    question: str = Field(..., min_length=1)
    answer: str = Field(..., min_length=1)
    rating: int = Field(..., description="1 = thumbs up, -1 = thumbs down")

    @field_validator("rating")
    @classmethod
    def rating_must_be_valid(cls, v: int) -> int:
        if v not in (1, -1):
            raise ValueError("Rating must be 1 or -1")
        return v


class FeedbackResponse(BaseModel):
    """Response for POST /feedback."""

    success: bool = True
    message: str = "Feedback saved"