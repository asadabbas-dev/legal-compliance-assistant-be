"""Feedback endpoint - thumbs up/down on answers."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.auth.deps import get_optional_current_user
from app.models import Feedback
from app.models import User
from app.schemas.feedback import FeedbackRequest, FeedbackResponse
from app.services.user_service import get_or_create_anonymous_user

router = APIRouter(prefix="/feedback", tags=["feedback"])


@router.post("", response_model=FeedbackResponse)
def submit_feedback(
    body: FeedbackRequest,
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_optional_current_user),
):
    """Save user feedback (thumbs up/down) on an answer."""
    actor = current_user or get_or_create_anonymous_user(db)
    feedback = Feedback(
        user_id=actor.id,
        question=body.question,
        answer=body.answer,
        rating=body.rating,
    )
    db.add(feedback)
    db.commit()
    return FeedbackResponse(success=True, message="Feedback saved")
