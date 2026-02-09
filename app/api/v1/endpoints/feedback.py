"""Feedback endpoint - thumbs up/down on answers."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.models import Feedback
from app.schemas.feedback import FeedbackRequest, FeedbackResponse

router = APIRouter(prefix="/feedback", tags=["feedback"])


@router.post("", response_model=FeedbackResponse)
def submit_feedback(
    body: FeedbackRequest,
    db: Session = Depends(get_db),
):
    """Save user feedback (thumbs up/down) on an answer."""
    feedback = Feedback(
        question=body.question,
        answer=body.answer,
        rating=body.rating,
    )
    db.add(feedback)
    db.commit()
    return FeedbackResponse(success=True, message="Feedback saved")
