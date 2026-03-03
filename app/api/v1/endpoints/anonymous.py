"""Anonymous user endpoints."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.auth.jwt import create_access_token
from app.services.user_service import get_or_create_anonymous_user

router = APIRouter(prefix="/anonymous", tags=["anonymous"])


@router.post("/token")
def get_anonymous_token(db: Session = Depends(get_db)):
    """Get an anonymous token for guest users."""
    anonymous_user = get_or_create_anonymous_user(db)
    return {
        "access_token": create_access_token(anonymous_user.id),
        "token_type": "bearer",
        "user_id": str(anonymous_user.id),
    }